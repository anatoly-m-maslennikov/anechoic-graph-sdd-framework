"""Admit Worker generations through the private Kernel socket."""

import http.client
from contextlib import closing
import json
import re
import stat
import sys
from pathlib import Path
from urllib.parse import urlencode

from ORCHESTRATOR_beta_C68.generation.generation_admission import (
    CompilerColumnsChanged as CompilerColumnsChanged,
    DeltaRequiresReconciliation as DeltaRequiresReconciliation,
    GenerationBaseChanged,
    WorkerIngestionFailure as WorkerIngestionFailure,
    _admission_error,
    _admission_payload,
    _admitted_result,
    wait_build as wait_build,
    worker_failure as worker_failure,
)
from ORCHESTRATOR_beta_C68.jobs import UnixConnection
from ORCHESTRATOR_beta_C68.generation.worker.checkpoint.startup_checkpoint import CHECKPOINT_FIELDS, MAX_DELTA_PATHS, ReuseRecord
from ORCHESTRATOR_beta_C68.generation.worker.worker_reply import parse_worker_result as parse_worker_result

REUSE_FIELDS = {"inputs", "graph_config", "endpoints"}
TICKET_ROOTS = {"__TICKETS", "001_TICKETS", "__TKT"}
MAX_WARM_DELTA_PATHS = 32


def replace_ingestion_issues(
    socket_path, instance_id, source, issues, *, model_diagnostics=None
):
    data = {"instance_id": instance_id, "source": source, "issues": issues}
    if model_diagnostics is not None:
        data["model_diagnostics"] = model_diagnostics
    payload = json.dumps(data, ensure_ascii=False)
    with closing(UnixConnection(socket_path)) as connection:
        connection.request(
            "PUT",
            "/ingestion/issues",
            payload.encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body = response.read()
        if response.status != 200:
            raise RuntimeError(
                "Kernel rejected ingestion issues: "
                + body.decode("utf-8", "replace")[:2048]
            )


def ticket_delta_paths(binding, changes):
    root = Path(binding["root"])
    control = root / binding["control_root"]
    if (
        not control.name.startswith(("_anechoic_", "."))
        or not control.is_dir()
    ):
        return None
    ticket = re.compile(
        (
            f"{re.escape(binding['project_prefix'])}"
            "-T-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?[-.].*\\.md\\Z"
        )
    )
    paths = set()
    for change in changes:
        if (
            not isinstance(change, dict)
            or change.get("is_directory") is not False
        ):
            return None
        event = change.get("event_type")
        source, destination = change.get("old_path"), change.get("new_path")
        if event == "moved":
            if destination == source:
                return None
            endpoints = (source, destination)
        elif event in ("created", "deleted", "modified") and destination in (
            None,
            "",
        ):
            endpoints = (source,)
        else:
            return None
        for value in endpoints:
            relative = _ticket_path(root, control, ticket, value)
            if relative is None:
                return None
            paths.add(relative)
            if len(paths) > MAX_DELTA_PATHS:
                return None
    return sorted(paths) or None


def _ticket_path(root, control, ticket, value):
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if (
        not path.is_absolute()
        or str(path) != value
        or ".." in path.parts
        or not ticket.fullmatch(path.name)
        or not path.is_relative_to(control)
    ):
        return None
    parts = path.relative_to(control).parts
    relative = path.relative_to(root).as_posix()
    if len(parts) < 2 or parts[0] not in TICKET_ROOTS or "\\" in relative:
        return None
    try:
        if path.resolve() != path:
            return None
        if not stat.S_ISREG(path.lstat().st_mode):
            return None
    except FileNotFoundError:
        pass
    except OSError, ValueError, RuntimeError:
        return None
    return relative


def live_reuse(socket_path, instance_id, generation, result, prior, witness):
    carrier_delta = (
        "paths" in result
        and "compiler" not in result
        and "reuse" not in result
        and prior is not None
        and result.get("base_generation") == prior.get("base_generation")
        and isinstance(prior.get("status_domains"), dict)
    )
    if result.get("unchanged") is True or carrier_delta:
        domains = witness.get("status_domains")
    else:
        admitted = read_reuse(socket_path, instance_id)
        domains = (
            admitted.status_domains
            if admitted is not None and admitted.base_generation == generation
            else None
        )
    fields = {
        key: value
        for key, value in witness.items()
        if key not in CHECKPOINT_FIELDS | {"status_domains"}
    }
    fields["base_generation"] = generation
    if domains is not None:
        fields["status_domains"] = domains
    return ReuseRecord.model_validate(fields)


def read_reuse(socket_path, instance_id, scope=None):
    connection = None
    try:
        connection = UnixConnection(socket_path)
        connection.request(
            "GET",
            "/generation/reuse?"
            + urlencode(
                {"instance_id": instance_id}
                | ({"scope": scope} if scope else {})
            ),
        )
        response = connection.getresponse()
        if response.status != 200:
            return None
        result = json.loads(response.read())["result"]
        if (
            not isinstance(result, dict)
            or set(result) - CHECKPOINT_FIELDS - {"status_domains"}
            != REUSE_FIELDS | {"base_generation"}
            or not isinstance(result["base_generation"], str)
            or not result["base_generation"]
            or not isinstance(result["inputs"], dict)
            or not isinstance(result["endpoints"], dict)
            or (
                "archive_pending" in result
                and result["archive_pending"] is not True
            )
            or result.get("checkpoint_scope") != scope
            or any(
                key in result and not isinstance(result[key], dict)
                for key in ("carrier_hashes", "folder_hashes")
            )
        ):
            return None
        return ReuseRecord.model_validate(result)
    except OSError, ValueError, TypeError, KeyError, http.client.HTTPException:
        return None
    finally:
        if connection is not None:
            connection.close()


def read_accepted_model(socket_path, instance_id):
    with closing(UnixConnection(socket_path)) as connection:
        connection.request(
            "GET", "/model?" + urlencode({"instance_id": instance_id})
        )
        response = connection.getresponse()
        if response.status == 409:
            try:
                reason = (
                    json.loads(response.read()).get("error", {}).get("message")
                )
            except AttributeError, ValueError:
                reason = None
            print(
                (
                    "Using the bundled Model: "
                    f"{reason or 'Project Model asset is unavailable'}"
                ),
                file=sys.stderr,
            )
            return None
        if response.status != 200:
            raise ValueError("Cannot retrieve the accepted Project Model")
        model = json.loads(response.read())
        if not isinstance(model, dict):
            raise ValueError("Invalid accepted Project Model")
        return model


def worker_request(binding, socket_path, instance_id, reuse, paths):
    witness = (
        None
        if reuse is None
        else {
            key: value
            for key, value in reuse.items()
            if key not in {"archive_pending", "checkpoint_scope"}
        }
    )
    request = {"binding": binding, "reuse": witness}
    if paths is not None:
        request["paths"] = paths
    elif reuse is not None and reuse.get("graph_config") is not None:
        structure = read_structure(socket_path, instance_id, reuse)
        if structure is not None:
            request["structure"] = structure
    return request


def read_structure(socket_path, instance_id, reuse):
    if reuse is None:
        return None
    connection = None
    try:
        connection = UnixConnection(socket_path)
        connection.request(
            "GET", "/structure?" + urlencode({"instance_id": instance_id})
        )
        response = connection.getresponse()
        if (
            response.status != 200
            or response.getheader("x-anechoic-generation")
            != reuse["base_generation"]
        ):
            return None
        structure = json.loads(response.read())
        return structure if isinstance(structure, dict) else None
    except OSError, ValueError, TypeError, KeyError, http.client.HTTPException:
        return None
    finally:
        if connection is not None:
            connection.close()


def confirm_reuse(socket_path, instance_id, result):
    if result.get("archive_pending") is True:
        return admit_generation(socket_path, instance_id, None, result, None)
    current = read_reuse(socket_path, instance_id)
    if current is None or current.base_generation != result["base_generation"]:
        raise GenerationBaseChanged(
            "Kernel generation changed during revalidation"
        )
    return {"generation": result["base_generation"], "kind": "reused"}


def admit_generation(
    socket_path,
    instance_id,
    directory,
    result,
    target,
    *,
    archive=False,
    force_graph=False,
):
    path, kind, payload = _admission_payload(
        instance_id, directory, result, target, archive, force_graph
    )
    connection = UnixConnection(socket_path)
    try:
        connection.request(
            "PUT",
            path,
            json.dumps(
                payload, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        body = response.read()
        if response.status != 200:
            raise _admission_error(response.status, body, kind)
        return _admitted_result(body, kind, target)
    finally:
        connection.close()
