"""Coordinate pinned trace, HTTP, shape and framing checks."""

from copy import deepcopy

from ._formal_chain_checks import (
    _check_observations,
    _comparison_gap,
    _evidence,
    _model_pin,
    _selected_profile,
    _supports_trace,
    _tool_api,
    _validated_pin,
)
from .LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SourceError
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_1_DIAGNOSTICS_C90._package__shared import finding  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    select_formal_claims
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    capture_lean_json, compile_lean
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_MERMAID_RENDERER_C87._package__shared import (
    render_solution
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_TEST_GENERATION_C92._package__shared import (
    build_python_framing_cases
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    compare_cli_spec,
    compare_shape_spec,
    compare_tool_api_spec,
    compare_trace_spec,
)  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_TRANSLATION_VALIDATOR_C86._package__shared import (
    validate_translation,
)  # fmt: skip


def _require_diagram(model, claim, observations, *, action=None):
    rendering = observations.setdefault("rendering", {})

    def observe(selected, selected_action):
        pin = _model_pin(selected)
        rendering.update(solution_pin=pin, action=selected_action)

    diagram = render_solution(model, claim, action=action, observe=observe)
    if not isinstance(diagram, str) or not diagram.strip():
        raise SourceError(
            "solution",
            model["solution"]["source"],
            "mermaid",
            "The selected Solution has no Mermaid diagram",
        )
    rendering["diagram_pin"] = _model_pin(diagram)
    return diagram


def _comparison_entry(model, claims, action):
    contract = claims.get("contract", {})
    solution = claims.get("solution")
    languages = [
        model[role]["claims"][0][0] for role in ("contract", "solution")
    ]
    if model.get("embedded_contract") and languages[1] == "python":
        profile = _selected_profile(contract, solution, action)
        if profile.get("transport") == "cli":
            return compare_cli_spec, {
                "interface": profile["interface"],
                "action": action,
            }
        if _tool_api(profile or contract):
            return compare_tool_api_spec, {"action": action}
    if languages[1] == "python" and _supports_trace(model, contract):
        message = _comparison_gap(contract, action)
        if message is not None:
            return None, finding(
                model["contract"]["source"], "action", message
            )
        return compare_trace_spec, {"action": action}
    if languages == ["python shape", "python shape"] and action is None:
        return compare_shape_spec, {}
    return None, finding(
        model["contract"]["source"],
        "contract",
        "Unsupported formal chain comparison",
    )


def _compare_validated(model, canonical, action, lean, observations):
    claims = canonical["claims"]
    entry, options = _comparison_entry(model, claims, action)
    if entry is None:
        return None, options

    def observe(actual_claims, actual_action, kind):
        observations["comparison"] = dict(
            claims_pin=_model_pin(actual_claims),
            action=actual_action,
            kind=kind,
        )

    diagram = _require_diagram(
        model, claims.get("solution"), observations, action=action
    )
    result = entry(
        model,
        canonical,
        lean=lean,
        mermaid=diagram,
        observe=observe,
        **options,
    )
    return result, None


def _compare_framing(model, canonical, action, observations):
    if action not in (None, "framing"):
        return None, finding(
            model["manifest"]["source"],
            "action",
            f"Unknown Contract Action {action!r}",
        )
    sources = {
        role: model[role]["source"] for role in ("manifest", "solution")
    }
    mermaid = _require_diagram(
        model, canonical["claims"]["solution"], observations
    )
    return {
        **canonical["framing_comparison"],
        "sources": sources,
        "mermaid": mermaid,
    }, None


def generate_framing_cases(root, component_id, manifest, solution):
    """Generate inputs and expectations from pinned framing Specs."""
    model = load_boundary_model(
        root, component_id, manifest, solution=solution
    )
    return build_python_framing_cases(select_formal_claims(model, "framing"))


def _translate(model, lean):
    compiled = compile_lean(deepcopy(model))
    generated_pin = (
        _model_pin(compiled["claims"]) if "claims" in compiled else None
    )
    direct_framing = model.get("embedded_contract") and all(
        [language for language, _ in model[role]["claims"]]
        == ["python framing"]
        for role in ("contract", "solution")
    )
    options = {"bounded_framing": True} if direct_framing else {}
    with capture_lean_json() as programs:
        translation = validate_translation(
            model, compiled["lean"], lean=lean, **options
        )
    return compiled, generated_pin, direct_framing, translation, programs


def _compare_selected(model, canonical, action, lean, direct_framing):
    roles = (
        ("manifest", "solution")
        if model.get("embedded_contract")
        else ("manifest", "contract", "solution")
    )
    sources = deepcopy({role: model[role]["source"] for role in roles})
    observations = {}
    with capture_lean_json() as programs:
        if direct_framing:
            result, gap = _compare_framing(
                model, canonical, action, observations
            )
        else:
            result, gap = _compare_validated(
                model, canonical, action, lean, observations
            )
    if gap is None:
        if result.get("sources") != sources:
            raise ValueError("Comparison source identities differ")
        diagram_pin = observations.get("rendering", {}).get("diagram_pin")
        if _model_pin(result.get("mermaid")) != diagram_pin:
            raise ValueError("Comparison diagram differs from renderer output")
    return result, gap, programs, observations


def _admit_translation(model, lean):
    compiled, generated_pin, direct_framing, translation, programs = (
        _translate(model, lean)
    )
    claims = translation.pop("claims", None)
    expected = "bounded_match" if direct_framing else "matched"
    if translation["status"] != expected:
        return translation, None
    if claims is None:
        raise ValueError("Missing validated Model claims")
    validated_pin = _validated_pin(
        programs, claims, generated_pin, model, compiled["lean"]
    )
    canonical = {**compiled, "claims": claims}
    solution_pin = _model_pin(claims["solution"])
    framing_pin = translation.pop("framing_result_pin", None)
    if direct_framing:
        if not framing_pin or "framing_comparison" not in translation:
            raise ValueError("Missing validated framing evidence")
        canonical["framing_comparison"] = translation.pop("framing_comparison")
    pins = (validated_pin, generated_pin, solution_pin, framing_pin)
    return translation, (canonical, direct_framing, programs, pins)


def _complete_comparison(model, translation, validated, action, lean):
    canonical, direct_framing, programs, pins = validated
    lean_source = canonical["lean"]
    validated_pin, generated_pin, solution_pin, framing_pin = pins
    comparison, gap, comparison_programs, observations = _compare_selected(
        model, canonical, action, lean, direct_framing
    )
    if gap is not None:
        return {
            "outcome": "incomplete",
            "translation": translation,
            "unresolved": [gap],
            "diagnostics": [gap],
        }
    _check_observations(
        observations,
        solution_pin,
        validated_pin,
        framing_pin,
        action,
        canonical["claims"],
        comparison,
    )
    evidence = _evidence(
        comparison,
        action,
        (programs, comparison_programs),
        observations,
        validated_pin,
        generated_pin,
    )
    return {
        "outcome": "compared",
        "translation": translation,
        "lean": lean_source,
        **comparison,
        "evidence": evidence,
    }


def _failure(error, source, stage):
    if isinstance(error, SourceError):
        source = error.source if isinstance(error.source, dict) else source
        problem = {
            **finding(source, error.field, str(error)),
            "role": error.role,
        }
    else:
        problem = finding(source, stage, str(error))
    return {"outcome": "incomplete", "diagnostics": [problem]}


def verify_formal_chain(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    action=None,
    lean="lean",
):
    """Check emitted declarations before comparing a pinned chain."""
    source, stage = manifest, "specification"
    try:
        model = select_formal_claims(
            load_boundary_model(
                root, component_id, manifest, contract, solution
            ),
            action,
        )
        source = model.get("manifest", {}).get("source", manifest)
        stage = "translation"
        translation, validated = _admit_translation(model, lean)
        if validated is None:
            return {
                "outcome": "incomplete",
                "translation": translation,
                "diagnostics": [
                    *translation["issues"],
                    *translation["unresolved"],
                ],
            }
        stage = "comparison"
        return _complete_comparison(
            model, translation, validated, action, lean
        )
    except (OSError, ValueError) as error:
        return _failure(error, source, stage)
