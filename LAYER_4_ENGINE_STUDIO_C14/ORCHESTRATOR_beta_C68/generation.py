"""Admit Worker generations through the private Kernel socket."""
import http.client
from contextlib import closing
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlencode

from .ticket_paths import TICKET_ROOTS as TICKET_ROOTS, _ticket_path as _ticket_path, ticket_delta_paths as ticket_delta_paths
from .jobs import UnixConnection
from .watcher_diagnostics import report_graph_consistency
from .startup_checkpoint import CHECKPOINT_FIELDS, MAX_DELTA_PATHS as MAX_DELTA_PATHS, checkpoint_paths

FULL_FIELDS = {"snapshot", "receipt", "graph", "reuse"}
NATIVE_FIELDS = {"base_generation", "snapshot", "snapshot_sha256"}
DELTA_FIELDS = NATIVE_FIELDS | {"paths"}
GRAPH_FIELDS = NATIVE_FIELDS | {"graph", "graph_sha256", "reuse"}
REUSE_FIELDS = {"inputs", "graph_config", "endpoints"}
MAX_WARM_DELTA_PATHS = 32


class GenerationBaseChanged(RuntimeError):
    """The Kernel no longer holds the native refresh base."""


class DeltaRequiresReconciliation(RuntimeError):
    """The Kernel refused a delta without admitting it."""


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


def ticket_allocation(socket_path, instance_id, base_generation, prefix):
    if re.fullmatch(r"[A-Z][A-Z0-9]*", prefix) is None:
        raise ValueError("Invalid Project prefix")
    sql = f"""WITH numbers AS (
        SELECT ltrim(regexp_extract(reference, '^{prefix}-T-([0-9]+)(@|$)', 1), '0') AS number
        FROM main.atoms WHERE starts_with(reference, '{prefix}-T-')
    )
    SELECT id, coalesce(nullif((SELECT arg_max(number, (length(number), number)) FROM numbers), ''), '0'),
        json_extract(model, '$.ticket_labels')::VARCHAR
    FROM main.generation"""
    request = json.dumps({"instance_id": instance_id, "sql": sql})
    with closing(UnixConnection(socket_path)) as connection:
        connection.request("POST", "/database", request, {"Content-Type": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("Kernel refused the Ticket allocation query")
        rows = json.loads(response.read())["result"]["rows"]
    if (not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], list)
            or len(rows[0]) != 3 or rows[0][0] != base_generation):
        raise ValueError("Kernel generation changed before Ticket allocation")
    number = rows[0][1]
    if not isinstance(number, str) or re.fullmatch(r"0|[1-9][0-9]*", number) is None:
        raise ValueError("Kernel returned an invalid Ticket number")
    if rows[0][2] is None:
        raise ValueError("The admitted Model lacks Ticket label rules")
    labels = json.loads(rows[0][2])
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        raise ValueError("Kernel returned invalid Ticket label rules")
    return number, labels


def read_reuse(socket_path, instance_id):
    connection = None
    try:
        connection = UnixConnection(socket_path)
        connection.request("GET", "/generation/reuse?" + urlencode({"instance_id": instance_id}))
        response = connection.getresponse()
        if response.status != 200:
            return None
        result = json.loads(response.read())["result"]
        if (not isinstance(result, dict)
                or set(result) - CHECKPOINT_FIELDS != REUSE_FIELDS | {"base_generation"}
                or not isinstance(result["base_generation"], str) or not result["base_generation"]
                or not isinstance(result["inputs"], dict) or not isinstance(result["endpoints"], dict)
                or ("archive_pending" in result and result["archive_pending"] is not True)
                or any(key in result and not isinstance(result[key], dict) for key in ("carrier_hashes", "folder_hashes"))):
            return None
        return result
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
            return None
        if response.status != 200:
            raise ValueError("Cannot retrieve the accepted Project Model")
        model = json.loads(response.read())
        if not isinstance(model, dict):
            raise ValueError("Invalid accepted Project Model")
        return model


def worker_request(binding, socket_path, instance_id, reuse, paths):
    witness = None if reuse is None else {key: value for key, value in reuse.items() if key != "archive_pending"}
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


def parse_worker_result(stdout, reuse, paths, structure=None, *, foreground=False):
    result = json.loads(stdout)
    if not isinstance(result, dict):
        raise TypeError("Worker returned invalid generation")
    fields = set(result) - {"carrier_hashes"}
    if "model_diagnostics" in fields:
        if not isinstance(result["model_diagnostics"], list):
            raise ValueError("Worker returned invalid Model diagnostics")
        fields.remove("model_diagnostics")
    if foreground and "deferred_archive" in fields:
        deferred = result["deferred_archive"]
        if (not isinstance(deferred, dict) or set(deferred) != {"roots", "snapshot", "carrier_hashes", "endpoints"}
                or not isinstance(deferred["roots"], list) or not isinstance(deferred["snapshot"], dict)
                or not isinstance(deferred["endpoints"], dict) or not isinstance(deferred["carrier_hashes"], dict)):
            raise ValueError("Worker returned invalid deferred archive input")
        fields.remove("deferred_archive")
    if "model_diagnostics" in result and fields != FULL_FIELDS:
        raise ValueError("Model diagnostics require a full generation")
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
    if fields != FULL_FIELDS or (foreground and "deferred_archive" not in result):
        raise ValueError("Worker returned invalid generation")
    witness = result["reuse"]
    if witness is not None and (not isinstance(witness, dict) or set(witness) != REUSE_FIELDS):
        raise ValueError("Worker returned invalid generation reuse witness")
    return result


def confirm_reuse(socket_path, instance_id, result):
    if result.get("archive_pending") is True:
        return admit_generation(socket_path, instance_id, None, result, None)
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


def _admission_route(result, archive):
    if archive:
        return "/generation/archive", "archive"
    if result.get("unchanged") is True:
        return "/generation/reuse", "reused"
    if "paths" in result:
        return "/generation/native-delta", "native_delta"
    if "base_generation" in result:
        return "/generation/native", "graph_refresh" if "graph" in result else "native_refresh"
    return "/generation", "full"


def admit_generation(socket_path, instance_id, directory, result, target, *, archive=False):
    path, kind = _admission_route(result, archive)
    payload = {"instance_id": instance_id, **result}
    if kind == "reused":
        del payload["unchanged"]
    if kind == "full":
        for field in ("model", "structure"):
            payload[field] = (Path(directory) / f"{field}.json").read_bytes().decode("utf-8")
    if target is not None:
        payload["refresh_target"] = target
    connection = UnixConnection(socket_path)
    try:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        connection.request("PUT", path, body,
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

