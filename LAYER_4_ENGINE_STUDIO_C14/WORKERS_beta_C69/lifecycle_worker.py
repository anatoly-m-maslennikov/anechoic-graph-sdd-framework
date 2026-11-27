"""Run one native lifecycle operation and capture its exact carrier delta."""
import json
from pathlib import Path
import sys
import tempfile

from .lifecycle_request import IndexedRequest, admit_cold_binding, admit_indexed, admit_request
from .managed_parent import watch_managed_parent
from .manifest_build_CS4.manifest_build_CS4__shared import manifest_input_signature
from .WORKERS_beta_C69__shared import _BuildFailure, _compile, _run_job, digest

_OWNER = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli"


def _carrier_effects(lifecycle):
    effects = lifecycle["effects"]
    if any(item.get("code") == "effect_uncertain" for item in lifecycle.get("errors", [])):
        raise ValueError("Native lifecycle reported an uncertain effect")
    final = {}
    for effect in effects:
        if effect.get("state") != "known" or effect.get("operation") not in {"create", "modify", "remove"}:
            raise ValueError("Native lifecycle reported an unsupported or unknown effect")
        if effect.get("evidence") in {"directory", "directory created", "directory absent after removal"}:
            continue
        final[effect["target"]] = effect
    if effects and not final:
        raise ValueError("Native lifecycle changed directories without carrier effects")
    return final


def _delta(binding, endpoints, base_generation, lifecycle, name, *, manifest_admitted=False, domains=None):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        capture_carrier_delta, capture_ticket_delta,
    )

    final = _carrier_effects(lifecycle)
    if not final:
        return None
    capture = capture_ticket_delta if name == "atom_lifecycle_direct_update" else capture_carrier_delta
    options = {"include_hashes": True}
    if domains is not None:
        options["domains"] = domains
    if manifest_admitted:
        options["manifest_admitted"] = True
    result = capture(binding, list(final), endpoints, **options)
    if result["snapshot"].get("ingestion_issues"):
        raise ValueError("Lifecycle carrier delta contains invalid Project files")
    hashes = result["carrier_hashes"]
    for path, effect in final.items():
        if (effect["operation"] == "remove" and path in hashes) or (
                effect["operation"] != "remove" and hashes.get(path) != effect["evidence"]):
            raise ValueError("Carrier delta does not match lifecycle effect receipt")
    return {"base_generation": base_generation, "snapshot_sha256": digest(result), **result}


def _validate_indexed(request):
    try:
        admitted = admit_request(request)
    except ValueError:
        raise ValueError("Invalid indexed lifecycle request") from None
    return admit_indexed(admitted)


def run(request, *, indexed_draft=None):
    if isinstance(request, IndexedRequest):
        return _run_indexed(request, indexed_draft=indexed_draft)
    request = admit_request(request)
    if request.model_fields_set & {"indexed_task", "lifecycle_context"}:
        return _run_indexed(admit_indexed(request), indexed_draft=indexed_draft)
    try:
        admitted_binding = admit_cold_binding(request.binding)
    except ValueError as error:
        raise _BuildFailure("manifest_build_CS4__shared", f"manifest_build_CS4__shared failed: {error}\n") from None
    binding = admitted_binding.model_dump()
    before = manifest_input_signature(binding)
    with tempfile.TemporaryDirectory(prefix="anechoic-lifecycle-") as temporary:
        root = Path(temporary).resolve()
        generation = root / "before"
        generation.mkdir()
        receipt, _, endpoints = _compile(binding, generation)
        if (receipt["structure_sha256"] != request.structure_sha256 or before is None
                or manifest_input_signature(binding) != before):
            return {"lifecycle": {"outcome": "failed"}, "delta": None,
                    "projection_error": "Lifecycle requires the admitted Model and Structure inputs"}
        payload = {"binding": binding, "name": request.name, "arguments": request.arguments}
        lifecycle = _run_job(_OWNER, {**payload, "generation": str(generation), "receipt": receipt})
        try:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import status_domains

            domains = status_domains(json.loads((generation / "model.json").read_bytes())["bindings"])
            delta = _delta(binding, endpoints, request.base_generation, lifecycle, request.name, domains=domains)
            if delta is not None and manifest_input_signature(binding) != before:
                observed = root / "after"
                observed.mkdir()
                after, _, _ = _compile(binding, observed)
                if after["structure_sha256"] != receipt["structure_sha256"]:
                    raise ValueError("Lifecycle changed the admitted Model or Structure")
            return {"lifecycle": lifecycle, "delta": delta, "projection_error": None}
        except Exception as error:
            return {"lifecycle": lifecycle, "delta": None, "projection_error": str(error) or type(error).__name__}

def _run_indexed(request, *, indexed_draft=None):
    binding = request.binding.model_dump()
    endpoints = request.indexed.endpoints
    indexed = {name: getattr(request.indexed, name) for name in type(request.indexed).model_fields if name != "endpoints"}
    payload = {"binding": binding, "name": request.name, "arguments": request.arguments, request.key: indexed}
    lifecycle = _run_job(_OWNER, payload) if indexed_draft is None else indexed_draft(payload)
    try:
        projected = getattr(request.indexed, "status_domains", None)
        domains = {family: set(values) for family, values in projected.items()} if projected is not None else None
        delta = _delta(binding, endpoints, request.base_generation, lifecycle, request.name,
                       manifest_admitted=True, domains=domains)
        return {"lifecycle": lifecycle, "delta": delta, "projection_error": None}
    except Exception as error:
        return {"lifecycle": lifecycle, "delta": None, "projection_error": str(error) or type(error).__name__}


def main():
    try:
        watch_managed_parent()
        print(json.dumps(run(json.load(sys.stdin)), ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
