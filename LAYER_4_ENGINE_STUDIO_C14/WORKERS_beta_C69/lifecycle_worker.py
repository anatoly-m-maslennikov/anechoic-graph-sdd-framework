"""Run one native lifecycle operation and capture its exact carrier delta."""
import json
from pathlib import Path
import sys
import tempfile

from .managed_parent import watch_managed_parent
from .manifest_build_CS4.manifest_build_CS4__shared import manifest_input_signature
from .WORKERS_beta_C69__shared import _compile, _run_job, digest

_OWNER = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli"


def _delta(binding, endpoints, base_generation, lifecycle, name, *, manifest_admitted=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        capture_carrier_delta, capture_ticket_delta,
    )

    effects = lifecycle["effects"]
    if any(item.get("code") == "effect_uncertain" for item in lifecycle.get("errors", [])):
        raise ValueError("Native lifecycle reported an uncertain effect")
    if not effects:
        return None
    final = {}
    for effect in effects:
        if effect.get("state") != "known" or effect.get("operation") not in {"create", "modify", "remove"}:
            raise ValueError("Native lifecycle reported an unsupported or unknown effect")
        if effect.get("evidence") in {"directory", "directory created", "directory absent after removal"}:
            continue
        final[effect["target"]] = effect
    if not final:
        raise ValueError("Native lifecycle changed directories without carrier effects")
    capture = capture_ticket_delta if name == "atom_lifecycle_direct_update" else capture_carrier_delta
    options = {"include_hashes": True}
    if manifest_admitted:
        options["manifest_admitted"] = True
    result = capture(binding, list(final), endpoints, **options)
    hashes = result["carrier_hashes"]
    for path, effect in final.items():
        if (effect["operation"] == "remove" and path in hashes) or (
                effect["operation"] != "remove" and hashes.get(path) != effect["evidence"]):
            raise ValueError("Carrier delta does not match lifecycle effect receipt")
    return {"base_generation": base_generation, "snapshot_sha256": digest(result), **result}


def run(request, *, indexed_draft=None):
    if (not isinstance(request, dict) or set(request) not in ({"binding", "name", "arguments", "base_generation", "structure_sha256"},
                                    {"binding", "name", "arguments", "base_generation", "structure_sha256", "indexed_task"})
            or ("indexed_task" in request and not isinstance(request["indexed_task"], dict))
            or not isinstance(request["name"], str) or not isinstance(request["arguments"], dict)
            or not isinstance(request["base_generation"], str) or not request["base_generation"]
            or not isinstance(request["structure_sha256"], str) or not request["structure_sha256"]):
        raise ValueError("Invalid lifecycle request")
    binding = request["binding"]
    if "indexed_task" in request:
        return _run_indexed(request, indexed_draft=indexed_draft)
    before = manifest_input_signature(binding)
    with tempfile.TemporaryDirectory(prefix="anechoic-lifecycle-") as temporary:
        root = Path(temporary).resolve()
        generation = root / "before"
        generation.mkdir()
        receipt, _, endpoints = _compile(binding, generation)
        if (receipt["structure_sha256"] != request["structure_sha256"] or before is None
                or manifest_input_signature(binding) != before):
            return {"lifecycle": {"outcome": "failed"}, "delta": None,
                    "projection_error": "Lifecycle requires the admitted Model and Structure inputs"}
        payload = {key: request[key] for key in ("binding", "name", "arguments")}
        lifecycle = _run_job(_OWNER, {**payload, "generation": str(generation), "receipt": receipt})
        try:
            delta = _delta(binding, endpoints, request["base_generation"], lifecycle, request["name"])
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
    indexed = request["indexed_task"]
    if (set(indexed) != {"max_number", "manifest_ref", "component_ids", "ticket_labels", "endpoints"}
            or any(not isinstance(indexed[key], str) or not indexed[key] for key in ("max_number", "manifest_ref"))
            or any(not isinstance(indexed[key], list) or any(not isinstance(item, str) for item in indexed[key])
                   for key in ("component_ids", "ticket_labels"))
            or not isinstance(indexed["endpoints"], dict)):
        raise ValueError("Invalid indexed task request")
    payload = {key: request[key] for key in ("binding", "name", "arguments")}
    payload["indexed_task"] = {key: value for key, value in indexed.items() if key != "endpoints"}
    lifecycle = _run_job(_OWNER, payload) if indexed_draft is None else indexed_draft(payload)
    try:
        delta = _delta(request["binding"], indexed["endpoints"], request["base_generation"], lifecycle,
                       request["name"], manifest_admitted=True)
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
