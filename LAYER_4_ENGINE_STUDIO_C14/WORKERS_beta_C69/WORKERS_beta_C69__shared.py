"""Build a transient, pinned Current Atom snapshot from an admitted binding."""

from __future__ import annotations
from functools import partial
from hashlib import sha256 as sha256
import json
import shutil as shutil
import sys
import subprocess as subprocess


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    NativeSnapshotChanged,
    status_domains,
)  # fmt: skip

from .spec_staging import _stage_spec_rows
from .worker_generation import _GenerationOptions, _build_generation
from .worker_graph import (
    _build_graph as _build_graph,
    _graph_only,
    _rebuild_graph,
)
from .worker_compile import (
    _BuildFailure as _BuildFailure,
    _compile_ingested,
    _read_compile_receipt,
    _run_job,
)
from .graph_consistency import _graph_consistency as _graph_consistency
from .managed_request import _managed_request
from .generation_batches import _capture_archive
from .python_code_units import python_code_units as python_code_units
from .python_context_restoration import (
    python_context_restoration as python_context_restoration,
)
from .python_import_order import python_import_order as python_import_order
from .native_refresh import (
    _domain_option,
    _reuse_hint,
    _ticket_delta,
    artifact_inputs as artifact_inputs,
    deferred_incremental,
    digest as digest,
    refresh,
    reusable_graph as reusable_graph,
    startup_incremental,
)

sys.dont_write_bytecode = True


def _capture(binding, endpoints=None, *, watcher_guarded=False, domains=None):
    if endpoints is not None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import (
            prepare_generation_snapshot,
        )  # fmt: skip

        config, finish = prepare_generation_snapshot(
            binding,
            include_hashes=True,
            watcher_guarded=watcher_guarded,
            domains=domains,
        )
        snapshot, hashes = finish(endpoints)
        return {
            "snapshot": snapshot,
            "graph_config": config,
            "carrier_hashes": hashes,
        }
    request = binding
    capture = _run_job(
        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli",
        request,
    )
    if not isinstance(capture, dict) or set(capture) != {
        "snapshot",
        "stability_sha256",
        "graph_config",
    }:
        raise ValueError("Invalid native capture response")
    return capture


def build(binding):
    return _capture(binding)["snapshot"]


def _compile(binding, stage):
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    receipt = _run_job(module, binding, "--output-dir", str(stage))
    return _read_compile_receipt(binding, stage, receipt)


class _ModelAttemptFailure(ValueError):
    def __init__(self, error, diagnostics):
        super().__init__(str(error))
        self.model_diagnostics = diagnostics


def _compile_and_capture(
    binding, stage, model_inputs, model_source, finish_snapshot
):
    if model_source is not None and "spec_database" in model_source:
        model_inputs = _stage_spec_rows(
            binding, model_inputs, model_source["spec_database"]
        )
    compiled = (
        _compile(binding, stage)
        if model_source is None
        else _compile_ingested(binding, stage, model_inputs, model_source)
    )
    try:
        captured = finish_snapshot(
            compiled[2],
            status_domains(
                json.loads((stage / "model.json").read_text())["bindings"]
            ),
        )
    except NativeSnapshotChanged:
        raise
    except ValueError as error:
        if model_source is None:
            raise
        if compiled[3]:
            raise _ModelAttemptFailure(error, compiled[3]) from error
        compiled = _compile_ingested(
            binding,
            stage,
            model_inputs,
            model_source,
            fallback=error,
            diagnostics=compiled[3],
        )
        try:
            captured = finish_snapshot(
                compiled[2],
                status_domains(
                    json.loads((stage / "model.json").read_text())["bindings"]
                ),
            )
        except (OSError, RuntimeError, TypeError, ValueError) as failure:
            raise _ModelAttemptFailure(failure, compiled[3]) from failure
    return compiled, captured


def build_generation(
    binding,
    output,
    *,
    managed=False,
    watcher_guarded=False,
    foreground=False,
    replay_graph=False,
    model_source=None,
    batch_full=False,
    defer_graph=False,
    domains=None,
):
    options = _GenerationOptions(
        managed,
        watcher_guarded,
        foreground,
        replay_graph,
        model_source,
        batch_full,
        defer_graph,
        domains,
    )
    return _build_generation(binding, output, _compile_and_capture, options)


def _try_refresh(admitted, binding, reuse, foreground, guarded, incremental):
    if (foreground or admitted.defer_graph) and admitted.paths is not None:
        native = _ticket_delta(binding, reuse, admitted.paths)
        if native is not None:
            return native
    elif not admitted.defer_graph and (not foreground or incremental):
        native = refresh(
            binding,
            reuse,
            partial(_capture, watcher_guarded=guarded),
            admitted.paths,
            admitted.structure,
            partial(
                _rebuild_graph,
                watcher_guarded=guarded and not incremental,
                replay_graph=admitted.replay_graph,
            ),
            watcher_guarded=guarded,
            incremental=incremental,
            foreground=foreground,
        )
        if native is not None:
            return native
    return None


def _is_managed_request(request):
    return (
        isinstance(request, dict)
        and "binding" in request
        and "reuse" in request
    )


def _run(request, output):
    if output is None:
        return build(request)
    if not _is_managed_request(request):
        return build_generation(request, output)
    admitted = _managed_request(request)
    binding, reuse = admitted.binding, _reuse_hint(admitted.reuse)
    guarded, foreground, incremental = (
        admitted.watcher_guarded,
        admitted.foreground,
        admitted.incremental,
    )
    if admitted.graph_only:
        return _graph_only(
            binding, reuse, admitted.structure, guarded, admitted.force_graph
        )
    if "archive" in admitted.model_fields_set:
        return _run_archive(
            admitted, binding, reuse, guarded, incremental, output
        )
    native = _deferred_result(
        admitted, binding, reuse, foreground, guarded, incremental, output
    )
    if native is not None:
        return native
    native = _try_refresh(
        admitted, binding, reuse, foreground, guarded, incremental
    )
    if native is not None:
        return native
    return build_generation(
        binding,
        output,
        managed=True,
        watcher_guarded=guarded,
        foreground=foreground,
        replay_graph=admitted.replay_graph,
        model_source=admitted.model_source,
        batch_full=admitted.batch_full,
        defer_graph=admitted.defer_graph,
        **(_domain_option(reuse) if reuse is not None else {}),
    )


def _deferred_result(
    admitted, binding, reuse, foreground, guarded, incremental, output
):
    if admitted.defer_graph and incremental and admitted.paths is None:
        compile_artifacts = _compile if admitted.model_source is None else None
        return deferred_incremental(
            binding, reuse, foreground, guarded, output, compile_artifacts
        )
    return None


def _run_archive(admitted, binding, reuse, guarded, incremental, output):
    if incremental:
        return startup_incremental(
            binding,
            reuse,
            archive_roots=admitted.archive.roots,
            watcher_guarded=guarded,
        )
    return _capture_archive(
        binding,
        admitted.archive,
        guarded,
        output if admitted.batch_full else None,
        **(_domain_option(reuse) if reuse is not None else {}),
    )


def main():
    from .worker_entry import main as run

    return run(_run)


if __name__ == "__main__":
    raise SystemExit(main())
