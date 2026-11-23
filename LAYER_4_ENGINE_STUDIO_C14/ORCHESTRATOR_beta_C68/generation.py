"""Admit Worker generations through the private Kernel socket."""
import http.client
import json
import re
import stat
from pathlib import Path, PurePosixPath
from urllib.parse import urlencode

from .jobs import UnixConnection

FULL_FIELDS = {"snapshot", "receipt", "graph", "reuse"}
NATIVE_FIELDS = {"base_generation", "snapshot", "snapshot_sha256"}
DELTA_FIELDS = NATIVE_FIELDS | {"paths"}
GRAPH_FIELDS = NATIVE_FIELDS | {"graph", "graph_sha256", "reuse"}
REUSE_FIELDS = {"inputs", "graph_config", "endpoints"}
TICKET_ROOTS = {"__TICKETS", "001_TICKETS", "__TKT"}
MAX_DELTA_PATHS = 1024
MAX_WARM_DELTA_PATHS = 32


class GenerationBaseChanged(RuntimeError):
    """The Kernel no longer holds the native refresh base."""


class DeltaRequiresReconciliation(RuntimeError):
    """The Kernel refused a delta without admitting it."""


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


def read_reuse(socket_path, instance_id):
    connection = None
    try:
        connection = UnixConnection(socket_path)
        connection.request("GET", "/generation/reuse?" + urlencode({"instance_id": instance_id}))
        response = connection.getresponse()
        if response.status != 200:
            return None
        result = json.loads(response.read())["result"]
        if (not isinstance(result, dict) or set(result) not in (REUSE_FIELDS | {"base_generation"}, REUSE_FIELDS | {"base_generation", "carrier_hashes"})
                or not isinstance(result["base_generation"], str) or not result["base_generation"]
                or not isinstance(result["inputs"], dict) or not isinstance(result["endpoints"], dict)
                or ("carrier_hashes" in result and not isinstance(result["carrier_hashes"], dict))):
            return None
        return result
    except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException):
        return None
    finally:
        if connection is not None:
            connection.close()


def worker_request(binding, socket_path, instance_id, reuse, paths):
    request = {"binding": binding, "reuse": reuse}
    if paths is not None:
        request["paths"] = paths
    else:
        structure = read_structure(socket_path, instance_id, reuse)
        if structure is not None:
            request["structure"] = structure
    return request


def read_structure(socket_path, instance_id, reuse):
    if reuse is None or reuse.get("graph_config") is None:
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


def parse_worker_result(stdout, reuse, paths, structure=None):
    result = json.loads(stdout)
    if not isinstance(result, dict):
        raise TypeError("Worker returned invalid generation")
    fields = set(result) - {"carrier_hashes"}
    checkpoint = reuse is not None and "carrier_hashes" in reuse and paths is None
    if fields == {"base_generation", "unchanged"}:
        if not checkpoint or result.get("unchanged") is not True or result["base_generation"] != reuse["base_generation"] or "carrier_hashes" in result:
            raise ValueError("Worker returned invalid unchanged generation")
        return result
    if fields in (NATIVE_FIELDS, DELTA_FIELDS, GRAPH_FIELDS):
        if reuse is None or result["base_generation"] != reuse["base_generation"]:
            raise ValueError("Worker returned an unexpected generation base")
        if fields == GRAPH_FIELDS:
            witness = result["reuse"]
            if structure is None or not isinstance(witness, dict) or set(witness) != REUSE_FIELDS:
                raise ValueError("Worker returned invalid graph refresh")
        if fields == DELTA_FIELDS:
            relatives = sorted(map(PurePosixPath, paths or ()))
            expected = [[path.parent.as_posix(), path.name] for path in relatives]
            if checkpoint:
                expected = checkpoint_paths(result["paths"])
            if not expected or result["paths"] != expected:
                raise ValueError("Worker returned unexpected Ticket delta paths")
        return result
    if fields != FULL_FIELDS:
        raise ValueError("Worker returned invalid generation")
    witness = result["reuse"]
    if witness is not None and (not isinstance(witness, dict) or set(witness) != REUSE_FIELDS):
        raise ValueError("Worker returned invalid generation reuse witness")
    return result


def checkpoint_paths(paths):
    if not isinstance(paths, list) or not 0 < len(paths) <= MAX_DELTA_PATHS:
        return None
    result = []
    for pair in paths:
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) and x for x in pair):
            return None
        parent, name = pair
        path = PurePosixPath(parent) / name
        if ("\\" in parent or "\\" in name or path.is_absolute() or ".." in path.parts
                or path.parent.as_posix() != parent or path.name != name):
            return None
        result.append(pair)
    return result if result == sorted(result) and len({tuple(pair) for pair in result}) == len(result) else None


def confirm_reuse(socket_path, instance_id, result):
    current = read_reuse(socket_path, instance_id)
    if current is None or current["base_generation"] != result["base_generation"]:
        raise GenerationBaseChanged("Kernel generation changed during revalidation")
    return {"generation": result["base_generation"], "kind": "reused"}


def _admission_error(status, body, kind):
    message = "Kernel rejected generation: " + body.decode("utf-8", "replace")[:2048]
    if kind != "full" and status == 409:
        try:
            code = json.loads(body)["error"]["code"]
        except (ValueError, TypeError, KeyError):
            code = None
        if code == "generation_base_changed":
            return GenerationBaseChanged(message)
        if kind == "native_delta" and code == "delta_full_reconciliation":
            return DeltaRequiresReconciliation(message)
    return RuntimeError(message)


def admit_generation(socket_path, instance_id, directory, result, target):
    payload = {"instance_id": instance_id, **result}
    if "paths" in result:
        path, kind = "/generation/native-delta", "native_delta"
    elif "base_generation" in result:
        path, kind = "/generation/native", "graph_refresh" if "graph" in result else "native_refresh"
    else:
        path, kind = "/generation", "full"
        for field in ("model", "structure"):
            payload[field] = (Path(directory) / f"{field}.json").read_bytes().decode("utf-8")
    if target is not None:
        payload["refresh_target"] = target
    connection = UnixConnection(socket_path)
    try:
        connection.request("PUT", path, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
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
    if not job["event"].wait(timeout):
        return 504, {"error": {"code": "generation_timeout", "message": "Generation deadline exceeded"}}
    outcome = job["outcome"]
    if outcome is None:
        return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
    if outcome["state"] != "succeeded":
        return 502, {"error": {"code": outcome["code"], "message": outcome.get("message", "Generation failed")}}
    result = {"generation": outcome["generation"]}
    if job["target"] is not None:
        result["result_ids"] = outcome["result_ids"]
    return 200, {"result": result}

