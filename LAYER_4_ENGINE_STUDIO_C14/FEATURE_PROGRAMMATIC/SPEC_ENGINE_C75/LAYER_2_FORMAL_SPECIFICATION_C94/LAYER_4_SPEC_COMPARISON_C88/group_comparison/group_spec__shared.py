# fmt: off
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import (
    _count,
    _names,
)
# fmt: on
from ...LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution

from ..top_down__pub import compare_obligations


def _facts(claim):
    return {
        "children": sorted(set(claim["roles"].values())),
        **(
            {"entry_points": sorted(claim["entry_points"])}
            if "entry_points" in claim
            else {}
        ),
        **(
            {"current_record_count": claim["current_record_count"]}
            if "current_record_count" in claim
            else {}
        ),
        **{f"role.{key}": value for key, value in claim["roles"].items()},
    }


def _count_gaps(model, facts, compiled):
    if any("current_record_count" in facts[role] for role in ("contract", "solution")):
        for role in ("manifest", "contract", "solution"):
            if "current_record_count" not in facts[role]:
                compiled["unresolved"].append(
                    {
                        "source": model[role]["source"],
                        "field": "current_record_count",
                        "message": "Current record count is absent",
                    }
                )


def _count_directions(facts, report):
    if any("current_record_count" in facts[role] for role in ("contract", "solution")):
        for left, right in (
            ("manifest", "contract"),
            ("manifest", "solution"),
            ("contract", "solution"),
        ):
            direction = report["directions"][f"{left}_{right}"]
            if (
                "current_record_count" not in facts[left]
                or "current_record_count" not in facts[right]
            ) and direction["status"] == "matched":
                direction["status"] = "unresolved"
        if report["status"] == "matched" and any(
            direction["status"] == "unresolved"
            for direction in report["directions"].values()
        ):
            report["status"] = "unresolved"


def _provider_facts(root, component_id, children, providers):
    from ...LAYER_2_SPEC_READING_C83._package__shared import load_manifest

    if not isinstance(providers, dict):
        raise TypeError("role providers must be a mapping")
    _names(list(providers), r"[A-Za-z][A-Za-z0-9_]*", "role names")
    facts, sources = {}, {}
    for role, provider in providers.items():
        if not isinstance(provider, dict) or set(provider) != {
            "component_id",
            "name",
            "manifest",
        }:
            raise ValueError("invalid role provider")
        child_id, name, pin = (
            provider[key] for key in ("component_id", "name", "manifest")
        )
        _names([child_id], r"C[0-9]+", "Component ID")
        if (
            child_id not in children
            or not isinstance(name, str)
            or not name.strip()
            or not isinstance(pin, dict)
            or "sha256" not in pin
        ):
            raise ValueError("invalid child identity or unpinned Manifest")
        child = load_manifest(root, child_id, pin)
        if child["source"]["container_component"] != component_id:
            raise ValueError(f"{child_id} is not a direct child of {component_id}")
        if child["fields"].get("name") != name:
            raise ValueError(f"{child_id} does not match the expected name")
        facts[f"role.{role}"] = child_id
        sources[role] = child["source"]
    return facts, sources


def _add_providers(root, component_id, children, providers, compiled, facts, model):
    if providers is None:
        return "not_selected", {}
    selected, sources = _provider_facts(root, component_id, children, providers)
    facts["manifest"].update(selected)
    claimed = {
        f"role.{key}"
        for claim in compiled["claims"].values()
        for key in claim.get("roles", {})
    }
    if set(selected) == claimed and set(selected.values()) == set(children):
        return "complete", sources
    compiled["unresolved"].append(
        {
            "source": model["manifest"]["source"],
            "field": "role_providers",
            "message": "Role provider coverage is incomplete",
        }
    )
    return "partial", sources


def _server_facts(model, facts, compiled):
    boundaries = model["manifest"].get("boundaries")
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    server = io.get("server") if isinstance(io, dict) else None
    if isinstance(server, dict):
        try:
            facts["manifest"]["entry_points"] = sorted(
                _names(list(server), r"[A-Za-z][A-Za-z0-9_]*", "entry points")
            )
        except ValueError:
            server = None
    if not isinstance(server, dict):
        compiled["unresolved"].append(
            {
                "source": model["manifest"]["source"],
                "field": "boundaries.io.server",
                "message": ("Direct server entry points are absent or unsupported"),
            }
        )


def _group_facts(model, compiled, children):
    claims = compiled["claims"]
    facts = {
        role: _facts(claims[role]) if role in claims and "roles" in claims[role] else {}
        for role in ("contract", "solution")
    }
    for role in ("contract", "solution"):
        if (
            role in claims
            and "roles" in claims[role]
            and "entry_points" not in claims[role]
        ):
            compiled["unresolved"].append(
                {
                    "source": model[role]["source"],
                    "field": "entry_points",
                    "message": "Direct server entry points are absent",
                }
            )
    facts["manifest"] = {"children": sorted(children)}
    return facts


def _compare_group_facts(model, compiled, facts, lean):
    _count_gaps(model, facts, compiled)
    _server_facts(model, facts, compiled)
    sources = {
        role: model[role]["source"] for role in ("manifest", "contract", "solution")
    }
    report = compare_obligations(sources, facts, lean=lean)
    _count_directions(facts, report)
    if report["status"] == "matched" and (compiled["issues"] or compiled["unresolved"]):
        report["status"] = "unresolved"
    return report


def check_group_spec(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    structure_children,
    role_providers=None,
    current_record_count=None,
    lean="lean",
):
    """Compare declarations with children and optional role identity witnesses.

    Each role provider supplies component_id, exact name, and a SHA-pinned
    Manifest. The caller selects the role independently of the group claims.
    """
    from ...LAYER_2_SPEC_READING_C83._package__shared import (
        load_boundary_model,
    )
    from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean

    _names([component_id], r"C[0-9]+", "group Component ID")
    children = _names(structure_children, r"C[0-9]+", "Structure children")
    if component_id in children:
        raise ValueError("group cannot be its own direct child")
    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    facts = _group_facts(model, compiled, children)
    coverage, provider_sources = _add_providers(
        root, component_id, children, role_providers, compiled, facts, model
    )
    if current_record_count is not None:
        facts["manifest"]["current_record_count"] = _count(current_record_count)
    report = _compare_group_facts(model, compiled, facts, lean)
    report.update(
        role_provider_coverage=coverage,
        role_provider_sources=provider_sources,
        structure_children=children,
        issues=compiled["issues"],
        unresolved=compiled["unresolved"],
        mermaid=render_solution(model, compiled["claims"].get("solution")),
        lean=compiled["lean"],
    )
    from .._package__shared import report_comparison

    return report_comparison(model, report)
