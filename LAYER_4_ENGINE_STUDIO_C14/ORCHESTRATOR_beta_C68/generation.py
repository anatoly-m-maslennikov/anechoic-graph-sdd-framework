"""Admit Worker generations through the private Kernel socket."""
import http.client
from contextlib import closing
import json
import re
import stat
import sys
from pathlib import Path
from urllib.parse import urlencode

from .jobs import UnixConnection
from .watcher_diagnostics import report_graph_consistency
from .startup_checkpoint import CHECKPOINT_FIELDS, MAX_DELTA_PATHS, ReuseRecord
from .worker_reply import parse_worker_result as parse_worker_result

REUSE_FIELDS = {"inputs", "graph_config", "endpoints"}
TICKET_ROOTS = {"__TICKETS", "001_TICKETS", "__TKT"}
MAX_WARM_DELTA_PATHS = 32



class GenerationBaseChanged(RuntimeError):
    """The Kernel no longer holds the native refresh base."""


class DeltaRequiresReconciliation(RuntimeError):
    """The Kernel refused a delta without admitting it."""


class CompilerColumnsChanged(RuntimeError):
    """The candidate requires a different native projection layout."""


class WorkerIngestionFailure(RuntimeError):
    def __init__(self, message, diagnostic, model_diagnostics=None):
        super().__init__(message)
        self.diagnostic = diagnostic
        self.model_diagnostics = model_diagnostics


def worker_failure(stdout, detail, *, run_id=None):
    try:
        payload = json.loads(stdout)
        diagnostic = payload["ingestion_failure"]
        if (diagnostic["source"] in ("atom", "build") and isinstance(diagnostic["issues"], list)
                and diagnostic["issues"]):
            first_issue = diagnostic["issues"][0]
            if (diagnostic["source"] == "build" and isinstance(first_issue, dict)
                    and first_issue.get("code") == "realization_scan_failed"):
                report_graph_consistency(payload.get("graph_consistency"), run_id)
            model_diagnostics = payload.get("model_diagnostics")
            if model_diagnostics is not None and (diagnostic["source"] != "build" or not isinstance(model_diagnostics, list)):
                raise ValueError("Invalid Model diagnostics")
            return WorkerIngestionFailure("Worker failed: " + detail, diagnostic, model_diagnostics)
    except (TypeError, ValueError, KeyError):
        pass
    return RuntimeError("Worker failed: " + detail)


def replace_ingestion_issues(socket_path, instance_id, source, issues, *, model_diagnostics=None):
    data = {"instance_id": instance_id, "source": source, "issues": issues}
    if model_diagnostics is not None:
        data["model_diagnostics"] = model_diagnostics
    payload = json.dumps(data, ensure_ascii=False)
    with closing(UnixConnection(socket_path)) as connection:
        connection.request("PUT", "/ingestion/issues", payload.encode("utf-8"),
                           {"Content-Type": "application/json"})
        response = connection.getresponse()
        body = response.read()
        if response.status != 200:
            raise RuntimeError("Kernel rejected ingestion issues: " + body.decode("utf-8", "replace")[:2048])


def ticket_delta_paths(binding, changes):
    root = Path(binding["root"])
    control = root / binding["control_root"]
    if not control.name.startswith(("_anechoic_", ".")) or not control.is_dir():
        return None
    ticket = re.compile(rf"{re.escape(binding['project_prefix'])}-T-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z")
    paths = set()
    for change in changes:
        if not isinstance(change, dict) or change.get("is_directory") is not False:
            return None
        event = change.get("event_type")
        source, destination = change.get("old_path"), change.get("new_path")
        if event == "moved":
            if destination == source:
                return None
            endpoints = (source, destination)
        elif event in ("created", "deleted", "modified") and destination in (None, ""):
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
    if (not path.is_absolute() or str(path) != value or ".." in path.parts
            or not ticket.fullmatch(path.name) or not path.is_relative_to(control)):
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
    except (OSError, ValueError, RuntimeError):
        return None
    return relative


def live_reuse(socket_path, instance_id, generation, result, prior, witness):
    carrier_delta = ("paths" in result and "compiler" not in result and "reuse" not in result
                     and prior is not None and result.get("base_generation") == prior.get("base_generation")
                     and isinstance(prior.get("status_domains"), dict))
    if result.get("unchanged") is True or carrier_delta:
        domains = witness.get("status_domains")
    else:
        admitted = read_reuse(socket_path, instance_id)
        domains = admitted.status_domains if admitted is not None and admitted.base_generation == generation else None
    fields = {key: value for key, value in witness.items() if key not in CHECKPOINT_FIELDS | {"status_domains"}}
    fields["base_generation"] = generation
    if domains is not None:
        fields["status_domains"] = domains
    return ReuseRecord.model_validate(fields)


def read_reuse(socket_path, instance_id, scope=None):
    connection = None
    try:
        connection = UnixConnection(socket_path)
        connection.request("GET", "/generation/reuse?" + urlencode({"instance_id": instance_id} | ({"scope": scope} if scope else {})))
        response = connection.getresponse()
        if response.status != 200:
            return None
        result = json.loads(response.read())["result"]
        if (not isinstance(result, dict)
                or set(result) - CHECKPOINT_FIELDS - {"status_domains"} != REUSE_FIELDS | {"base_generation"}
                or not isinstance(result["base_generation"], str) or not result["base_generation"]
                or not isinstance(result["inputs"], dict) or not isinstance(result["endpoints"], dict)
                or ("archive_pending" in result and result["archive_pending"] is not True)
                or result.get("checkpoint_scope") != scope
                or any(key in result and not isinstance(result[key], dict) for key in ("carrier_hashes", "folder_hashes"))):
            return None
        return ReuseRecord.model_validate(result)
    except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException):
        return None
    finally:
        if connection is not None:
            connection.close()


def read_accepted_model(socket_path, instance_id):
    with closing(UnixConnection(socket_path)) as connection:
        connection.request("GET", "/model?" + urlencode({"instance_id": instance_id}))
        response = connection.getresponse()
        if response.status == 409:
            try:
                reason = json.loads(response.read()).get("error", {}).get("message")
            except (AttributeError, ValueError):
                reason = None
            print(f"Using the bundled Model: {reason or 'Project Model asset is unavailable'}",
                  file=sys.stderr)
            return None
        if response.status != 200:
            raise ValueError("Cannot retrieve the accepted Project Model")
        model = json.loads(response.read())
        if not isinstance(model, dict):
            raise ValueError("Invalid accepted Project Model")
        return model



def worker_request(binding, socket_path, instance_id, reuse, paths):
    witness = None if reuse is None else {key: value for key, value in reuse.items() if key not in {"archive_pending", "checkpoint_scope"}}
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
        connection.request("GET", "/structure?" + urlencode({"instance_id": instance_id}))
        response = connection.getresponse()
        if response.status != 200 or response.getheader("x-anechoic-generation") != reuse["base_generation"]:
            return None
        structure = json.loads(response.read())
        return structure if isinstance(structure, dict) else None
    except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException):
        return None
    finally:
        if connection is not None:
            connection.close()


def confirm_reuse(socket_path, instance_id, result):
    if result.get("archive_pending") is True:
        return admit_generation(socket_path, instance_id, None, result, None)
    current = read_reuse(socket_path, instance_id)
    if current is None or current.base_generation != result["base_generation"]:
        raise GenerationBaseChanged("Kernel generation changed during revalidation")
    return {"generation": result["base_generation"], "kind": "reused"}


def _admission_error(status, body, kind):
    message = "Kernel rejected generation: " + body.decode("utf-8", "replace")[:2048]
    if kind != "full" and status == 409:
        try:
            code = json.loads(body)["error"]["code"]
        except (ValueError, TypeError, KeyError):
            code = None
        if kind == "compiler_refresh" and code == "model_columns_changed":
            return CompilerColumnsChanged(message)
        if kind != "compiler_refresh" and code == "generation_base_changed":
            return GenerationBaseChanged(message)
        if kind in ("native_delta", "archive") and code == "delta_full_reconciliation":
            return DeltaRequiresReconciliation(message)
    return RuntimeError(message)


def _admission_route(result, archive):
    if archive:
        return "/generation/archive", "archive"
    if "compiler" in result:
        return "/generation/compiler", "compiler_refresh"
    if result.get("unchanged") is True:
        return "/generation/reuse", "reused"
    if "paths" in result:
        return "/generation/native-delta", "native_delta"
    if "base_generation" in result:
        return "/generation/native", "graph_refresh" if "graph" in result else "native_refresh"
    return "/generation", "full"


def admit_generation(socket_path, instance_id, directory, result, target, *, archive=False, force_graph=False):
    path, kind = _admission_route(result, archive)
    payload = {"instance_id": instance_id, **result}
    if force_graph:
        if kind != "graph_refresh" or "snapshot" in result:
            raise ValueError("Force requires graph-only admission")
        payload["force_graph"] = True
    if kind == "reused":
        del payload["unchanged"]
    if kind == "full":
        for field in ("model", "structure"):
            payload[field] = (Path(directory) / f"{field}.json").read_bytes().decode("utf-8")
    if kind in ("full", "archive") and "batch_artifact" in payload:
        artifact = Path(directory) / "generation-batches.jsonl"
        payload["batch_artifact"] = payload["batch_artifact"] | {"path": str(artifact)}
    if target is not None:
        payload["refresh_target"] = target
    connection = UnixConnection(socket_path)
    try:
        connection.request("PUT", path, json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                           {"Content-Type": "application/json"})
        response = connection.getresponse()
        body = response.read()
        if response.status != 200:
            raise _admission_error(response.status, body, kind)
        result = json.loads(body)["result"]
        if not isinstance(result["generation"], str) or not result["generation"]:
            raise ValueError("Kernel returned invalid generation result")
        admitted = {"generation": result["generation"], "kind": kind}
        if target is not None:
            if not isinstance(result["result_ids"], dict):
                raise ValueError("Kernel returned invalid generation result")
            admitted["result_ids"] = result["result_ids"]
        return admitted
    finally:
        connection.close()


def wait_build(job, timeout):
    if not job.event.wait(timeout):
        return 504, {"error": {"code": "generation_timeout", "message": "Generation deadline exceeded"}}
    outcome = job.outcome
    if outcome is None:
        return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
    if outcome["state"] != "succeeded":
        return 502, {"error": {"code": outcome["code"], "message": outcome.get("message", "Generation failed")}}
    result = {"generation": outcome["generation"]}
    if job.target is not None:
        result["result_ids"] = outcome["result_ids"]
    return 200, {"result": result}

