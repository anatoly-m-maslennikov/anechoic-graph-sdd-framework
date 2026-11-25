from ..LAYER_3_MERMAID_RENDERER_C87.solution_diagram__pub import render_solution
from .top_down__pub import compare_obligations

_UNRENDERED = object()


def check_shape_spec(root, component_id, manifest, contract, solution, *, lean='lean'):
    """Compare the pinned Contract against the observed Solution shape."""
    from ..LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model
    from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean

    model = load_boundary_model(root, component_id, manifest, contract, solution)
    return compare_shape_spec(model, compile_lean(model), lean=lean)


def compare_shape_spec(model, compiled, *, lean='lean', mermaid=_UNRENDERED):
    """Compare the normalized shape facts in a loaded chain."""
    claims = compiled['claims']
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get('solution'))
    required, observed = claims.get('contract'), claims.get('solution')
    contract_facts = {}
    solution_facts = {}
    if required and 'fields' in required:
        contract_facts = {'record': required['record'], 'subtype': required['subtype'], 'base': required['base'],
                          **{f'field.{key}': value for key, value in required['fields'].items()}}
        if observed and 'fields' in observed:
            solution_facts = {'record': observed['record'], 'subtype': observed['subtype'], 'base': observed['base'],
                              **{f'field.{key}': observed['fields'].get(key) for key in required['fields']}}
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    report = compare_obligations(sources, {'manifest': {}, 'contract': contract_facts, 'solution': solution_facts}, lean=lean)
    report.update(issues=compiled['issues'], unresolved=compiled['unresolved'], mermaid=mermaid, lean=compiled['lean'])
    return report
