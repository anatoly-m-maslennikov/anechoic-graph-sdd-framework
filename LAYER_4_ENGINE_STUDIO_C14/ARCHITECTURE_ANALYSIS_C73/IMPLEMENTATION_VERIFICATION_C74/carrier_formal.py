"""Bind the carrier to its Manifest, Contract, and Draft Solution."""

import hashlib
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        component_contract_fences,
        formal_claim_fences,
        parse_carrier,
        parse_component_manifest,
    )  # fmt: skip

_BASE = (
    "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
    "FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16/"
)
_PATHS = {
    "manifest": _BASE
    + (
        "01_TIER_1_ARCHITECTURE/AN-S-3069-SPEC-COMPONENT_MANIFEST--declare-ada"
        "pters.md"
    ),
    "solution": _BASE
    + (
        "ADAPTERS_C30/01_draft/AN-S-4742@2-draft-SWD-SOLUTION--extract-the-car"
        "rier-body.md"
    ),
}


def _carrier(root, name, identity, status):
    path = Path(root) / _PATHS[name]
    raw = path.read_bytes()
    parsed = parse_carrier(raw, path)
    meta = parsed.metadata
    state = meta.get("state", {})
    if (
        meta.get("atom_id") != identity
        or meta.get("atom_family") != "SPEC"
        or state.get("status") != status
        or type(state.get("version")) is not int
    ):
        raise ValueError("invalid " + name + " identity or state")
    evidence = {
        "path": _PATHS[name],
        "atom_id": identity,
        "status": status,
        "version": state["version"],
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return parsed, evidence


def _lean_block(parsed, evidence, *, embedded=False):
    fences = (
        component_contract_fences(parsed.body)
        if embedded
        else formal_claim_fences(parsed.body)
    )
    blocks = [text for lang, text in fences or () if lang == "lean"]
    if len(blocks) != 1:
        raise ValueError(
            "expected exactly one Lean formal claim in " + evidence["atom_id"]
        )
    evidence["formal_sha256"] = hashlib.sha256(blocks[0].encode()).hexdigest()
    return blocks[0]


def _public_exports(fields):
    exports = fields.get("boundaries", {}).get("code", {}).get("exports", {})
    required = [
        "ADAPTERS_C30__shared." + name
        for name in ("frontmatter_bounds", "source_body")
    ]
    if fields.get("component_id") != "C30" or any(
        exports.get(name) != "public" for name in required
    ):
        raise ValueError("C30 Manifest does not expose the required symbols")
    return required


def _linked_source(root, pin, source, role):
    required = {"path", "atom_id", "version", "status", "container_component"}
    if (
        not isinstance(pin, dict)
        or pin.keys() - {"sha256"} != required
        or type(pin["version"]) is not int
        or pin["version"] < 1
        or any(
            not isinstance(pin[key], str) or not pin[key]
            for key in required - {"version"}
        )
        or not isinstance(source, dict)
        or source != {"sha256": source.get("sha256"), **pin}
        or type(source["version"]) is not int
    ):
        raise ValueError(f"{role} receipt does not match the requested pin")
    path = (root / pin["path"]).resolve()
    if path == root or not path.is_relative_to(root):
        raise ValueError(f"{role} source is outside the Project")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != source["sha256"]:
        raise ValueError(f"{role} bytes changed after formal comparison")
    return path, raw


def framing_exports(root, manifest, solution, sources):
    """Rebind the receipt to both sources and check framing operations."""
    root = Path(root).resolve()
    if not isinstance(sources, dict):
        raise ValueError("Formal receipt has no source pins")
    path, raw = _linked_source(
        root, manifest, sources.get("manifest"), "Manifest"
    )
    _linked_source(root, solution, sources.get("solution"), "Solution")
    fields = parse_component_manifest(parse_carrier(raw, path).body, tier=1)[0]
    exports = _public_exports(fields)
    io = fields["boundaries"].get("io")
    servers = io.get("server") if isinstance(io, dict) else None
    framing = (
        servers.get("carrier_body_framing")
        if isinstance(servers, dict)
        else None
    )
    operations = (
        framing.get("operations") if isinstance(framing, dict) else None
    )
    required = [name.split(".")[-1] for name in exports]
    if (
        not isinstance(operations, list)
        or len(operations) != len(required)
        or any(name not in operations for name in required)
    ):
        raise ValueError(
            "Manifest does not declare the two checked framing operations"
        )
    return exports


def formal_inputs(root):
    "Return independent claims and source pins, rejecting unbound carriers."
    manifest, me = _carrier(root, "manifest", "AN-S-3069", "active")
    solution, se = _carrier(root, "solution", "AN-S-4742", "draft")
    if (
        manifest.metadata.get("tier") != 1
        or manifest.metadata.get("context", {}).get("template")
        != "component_manifest"
    ):
        raise ValueError("invalid Manifest tier or template")
    _public_exports(parse_component_manifest(manifest.body, tier=1)[0])
    if (
        solution.metadata.get("container", {}).get("component") != "C30"
        or solution.metadata.get("tier") != 0
        or solution.metadata.get("context", {}).get("template") != "solution"
        or f"AN-S-3069@{me['version']}"
        not in solution.metadata.get("relations", {}).get("ANSWERS", [])
    ):
        raise ValueError("Solution binding does not match the active Manifest")
    ce = dict(me)
    blocks = [
        _lean_block(manifest, ce, embedded=True),
        _lean_block(solution, se),
    ]
    return blocks, {"manifest": me, "contract": ce, "solution": se}
