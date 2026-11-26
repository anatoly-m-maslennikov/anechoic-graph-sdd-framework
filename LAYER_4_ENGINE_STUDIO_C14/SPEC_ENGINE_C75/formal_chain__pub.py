"""Coordinate pinned trace and shape checks."""

from copy import deepcopy

from .LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import finding
from .LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import SourceError, load_boundary_model
from .LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from .LAYER_3_MERMAID_RENDERER_C87.solution_diagram__pub import render_solution
from .LAYER_4_SPEC_COMPARISON_C88.shape_spec__pub import compare_shape_spec
from .LAYER_4_SPEC_COMPARISON_C88.trace_spec__pub import compare_trace_spec
from .LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub import validate_translation


def verify_formal_chain(root, component_id, manifest, contract, solution, *, action=None, lean='lean'):
    """Check emitted declarations before comparing a pinned chain."""
    try:
        model = load_boundary_model(root, component_id, manifest, contract, solution)
        compiled = compile_lean(deepcopy(model))
        translation = validate_translation(model, compiled['lean'], lean=lean)
        claims = translation.pop('claims')
        if translation['status'] != 'matched':
            return {'outcome': 'incomplete', 'translation': translation}
        canonical = {**compiled, 'claims': claims}
        languages = [model[role]['claims'][0][0] for role in ('contract', 'solution')]
        if languages[1] == 'python' and any(language == 'python trace' for language, _ in model['contract']['claims']):
            mermaid = render_solution(model, claims.get('solution'))
            comparison = compare_trace_spec(model, canonical, action=action, lean=lean, mermaid=mermaid)
        elif languages == ['python shape', 'python shape'] and action is None:
            mermaid = render_solution(model, claims.get('solution'))
            comparison = compare_shape_spec(model, canonical, lean=lean, mermaid=mermaid)
        else:
            gap = finding(model['contract']['source'], 'contract', 'Unsupported formal chain comparison')
            return {'outcome': 'incomplete', 'translation': translation, 'unresolved': [gap]}
        return {'outcome': 'compared', 'translation': translation, 'lean': compiled['lean'], **comparison}
    except SourceError as error:
        return {'outcome': 'incomplete', 'diagnostics': [
            {**finding(error.source, error.field, str(error)), 'role': error.role}]}
    except (OSError, ValueError) as error:
        return {'outcome': 'incomplete', 'diagnostics': [str(error)]}
