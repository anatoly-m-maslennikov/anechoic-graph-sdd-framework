from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import _count, _names
from .direct_comparison import report_comparison
from .top_down__pub import compare_obligations


def _facts(claim):
    return {'children': sorted(set(claim['roles'].values())),
            **({'entry_points': sorted(claim['entry_points'])} if 'entry_points' in claim else {}),
            **({'current_record_count': claim['current_record_count']} if 'current_record_count' in claim else {}),
            **{f'role.{key}': value for key, value in claim['roles'].items()}}


def _count_gaps(model, facts, compiled):
    if any('current_record_count' in facts[role] for role in ('contract', 'solution')):
        for role in ('manifest', 'contract', 'solution'):
            if 'current_record_count' not in facts[role]:
                compiled['unresolved'].append({'source': model[role]['source'], 'field': 'current_record_count',
                                               'message': 'Current record count is absent'})


def _count_directions(facts, report):
    if any('current_record_count' in facts[role] for role in ('contract', 'solution')):
        for left, right in (('manifest', 'contract'), ('manifest', 'solution'), ('contract', 'solution')):
            direction = report['directions'][f'{left}_{right}']
            if (('current_record_count' not in facts[left] or 'current_record_count' not in facts[right])
                    and direction['status'] == 'matched'):
                direction['status'] = 'unresolved'
        if report['status'] == 'matched' and any(direction['status'] == 'unresolved'
                                                 for direction in report['directions'].values()):
            report['status'] = 'unresolved'


def check_group_spec(root, component_id, manifest, contract=None, solution=None, *,
                     structure_children, current_record_count=None, lean='lean'):
    """Compare pinned declarations with independently selected direct children."""
    from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
    from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean

    _names([component_id], r'C[0-9]+', 'group Component ID')
    children = _names(structure_children, r'C[0-9]+', 'Structure children')
    if component_id in children:
        raise ValueError('group cannot be its own direct child')
    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    claims = compiled['claims']
    facts = {role: _facts(claims[role]) if role in claims and 'roles' in claims[role] else {}
             for role in ('contract', 'solution')}
    for role in ('contract', 'solution'):
        if role in claims and 'roles' in claims[role] and 'entry_points' not in claims[role]:
            compiled['unresolved'].append({'source': model[role]['source'], 'field': 'entry_points',
                                           'message': 'Direct server entry points are absent'})
    facts['manifest'] = {'children': sorted(children)}
    if current_record_count is not None:
        facts['manifest']['current_record_count'] = _count(current_record_count)
    _count_gaps(model, facts, compiled)
    boundaries = model['manifest'].get('boundaries')
    io = boundaries.get('io') if isinstance(boundaries, dict) else None
    server = io.get('server') if isinstance(io, dict) else None
    if isinstance(server, dict):
        try:
            facts['manifest']['entry_points'] = sorted(_names(list(server), r'[A-Za-z][A-Za-z0-9_]*', 'entry points'))
        except ValueError:
            server = None
    if not isinstance(server, dict):
        compiled['unresolved'].append({'source': model['manifest']['source'], 'field': 'boundaries.io.server',
                                       'message': 'Direct server entry points are absent or unsupported'})
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    report = compare_obligations(sources, facts, lean=lean)
    _count_directions(facts, report)
    if report['status'] == 'matched' and (compiled['issues'] or compiled['unresolved']):
        report['status'] = 'unresolved'
    report.update(structure_children=children, issues=compiled['issues'], unresolved=compiled['unresolved'],
                  mermaid=render_solution(model, claims.get('solution')), lean=compiled['lean'])
    return report_comparison(model, report)
