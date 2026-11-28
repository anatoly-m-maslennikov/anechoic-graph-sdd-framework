"""Form Kernel admissions and decode generation replies."""

import json
from pathlib import Path

from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import report_graph_consistency


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
        if (
            diagnostic["source"] in ("atom", "build")
            and isinstance(diagnostic["issues"], list)
            and diagnostic["issues"]
        ):
            first_issue = diagnostic["issues"][0]
            if (
                diagnostic["source"] == "build"
                and isinstance(first_issue, dict)
                and first_issue.get("code") == "realization_scan_failed"
            ):
                report_graph_consistency(
                    payload.get("graph_consistency"), run_id
                )
            model_diagnostics = payload.get("model_diagnostics")
            if model_diagnostics is not None and (
                diagnostic["source"] != "build"
                or not isinstance(model_diagnostics, list)
            ):
                raise ValueError("Invalid Model diagnostics")
            return WorkerIngestionFailure(
                "Worker failed: " + detail, diagnostic, model_diagnostics
            )
    except TypeError, ValueError, KeyError:
        pass
    return RuntimeError("Worker failed: " + detail)


def _admission_error(status, body, kind):
    message = (
        "Kernel rejected generation: " + body.decode("utf-8", "replace")[:2048]
    )
    if kind != "full" and status == 409:
        try:
            code = json.loads(body)["error"]["code"]
        except ValueError, TypeError, KeyError:
            code = None
        if kind == "compiler_refresh" and code == "model_columns_changed":
            return CompilerColumnsChanged(message)
        if kind != "compiler_refresh" and code == "generation_base_changed":
            return GenerationBaseChanged(message)
        if (
            kind in ("native_delta", "archive")
            and code == "delta_full_reconciliation"
        ):
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
        return (
            "/generation/native",
            "graph_refresh" if "graph" in result else "native_refresh",
        )
    return "/generation", "full"


def _admitted_result(body, kind, target):
    result = json.loads(body)["result"]
    if not isinstance(result["generation"], str) or not result["generation"]:
        raise ValueError("Kernel returned invalid generation result")
    admitted = {"generation": result["generation"], "kind": kind}
    if target is not None:
        if not isinstance(result["result_ids"], dict):
            raise ValueError("Kernel returned invalid generation result")
        admitted["result_ids"] = result["result_ids"]
    return admitted


def wait_build(job, timeout):
    if not job.event.wait(timeout):
        return 504, {
            "error": {
                "code": "generation_timeout",
                "message": "Generation deadline exceeded",
            }
        }
    outcome = job.outcome
    if outcome is None:
        return 503, {
            "error": {
                "code": "orchestrator_stopping",
                "message": "Orchestrator is stopping",
            }
        }
    if outcome["state"] != "succeeded":
        return 502, {
            "error": {
                "code": outcome["code"],
                "message": outcome.get("message", "Generation failed"),
            }
        }
    result = {"generation": outcome["generation"]}
    if job.target is not None:
        result["result_ids"] = outcome["result_ids"]
    return 200, {"result": result}


def _admission_payload(
    instance_id, directory, result, target, archive, force_graph
):
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
            payload[field] = (
                (Path(directory) / f"{field}.json")
                .read_bytes()
                .decode("utf-8")
            )
    if kind in ("full", "archive") and "batch_artifact" in payload:
        artifact = Path(directory) / "generation-batches.jsonl"
        payload["batch_artifact"] = payload["batch_artifact"] | {
            "path": str(artifact)
        }
    if target is not None:
        payload["refresh_target"] = target
    return path, kind, payload
