from ..LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    manifest_shape,
)  # fmt: skip
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from ._direct_comparison import comparison_claims, report_comparison
from .top_down__pub import compare_obligations

_UNRENDERED = object()


def check_shape_spec(
    root, component_id, manifest, contract=None, solution=None, *, lean="lean"
):
    """Compare the pinned Contract against the observed Solution shape."""
    from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
    from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean

    model = load_boundary_model(
        root, component_id, manifest, contract, solution
    )
    return compare_shape_spec(model, compile_lean(model), lean=lean)


def _shape_facts(shape):
    if not shape or "fields" not in shape:
        return {}
    return {
        "record": shape["record"],
        "subtype": shape["subtype"],
        "base": shape["base"],
        **{f"field.{key}": value for key, value in shape["fields"].items()},
    }


def compare_shape_spec(
    model, compiled, *, lean="lean", mermaid=_UNRENDERED, observe=None
):
    """Compare the normalized shape facts in a loaded chain."""
    claims = comparison_claims(compiled, observe, None, "shape")
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get("solution"))
    required, observed = claims.get("contract"), claims.get("solution")

    manifest = claims.get("manifest")
    shape = manifest_shape(manifest.get("boundaries")) if manifest else None
    manifest_facts, contract_facts, solution_facts = (
        _shape_facts(shape),
        _shape_facts(required),
        _shape_facts(observed),
    )
    if observed and "fields" in observed:
        for key in manifest_facts.keys() | contract_facts.keys():
            solution_facts.setdefault(key, None)
    if required and "fields" in required:
        for key in manifest_facts:
            contract_facts.setdefault(key, None)
    sources = {
        role: model[role]["source"]
        for role in ("manifest", "contract", "solution")
    }
    report = compare_obligations(
        sources,
        {
            "manifest": manifest_facts,
            "contract": contract_facts,
            "solution": solution_facts,
        },
        lean=lean,
    )
    if report["status"] == "matched" and (
        compiled["issues"] or compiled["unresolved"]
    ):
        report["status"] = "unresolved"
    report.update(
        issues=compiled["issues"],
        unresolved=compiled["unresolved"],
        mermaid=mermaid,
        lean=compiled["lean"],
    )
    return report_comparison(model, report)
