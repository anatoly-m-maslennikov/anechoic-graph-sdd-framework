"""Compare explicitly selected group membership and entry points."""

import ast
import re

from .top_down__pub import compare_obligations


def _names(values, pattern, label):
    if (not isinstance(values, (list, tuple))
            or any(not isinstance(value, str) or not re.fullmatch(pattern, value) for value in values)
            or len(set(values)) != len(values)):
        raise ValueError(f'invalid or duplicate {label}')
    return list(values)


def parse_group(source, role):
    tree = ast.parse(source)
    expected = {'contract': 'declare_group_contract', 'solution': 'component_group'}.get(role)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        raise ValueError('expected one group declaration')
    call = tree.body[0].value
    if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name)
            or call.func.id != expected or call.args
            or 'roles' not in {key.arg for key in call.keywords}
            or {key.arg for key in call.keywords} - {'roles', 'entry_points', 'current_record_count'}
            or len(call.keywords) != len({key.arg for key in call.keywords})):
        raise ValueError('expected roles and optional entry_points and current_record_count')
    args = {key.arg: key.value for key in call.keywords}
    node = args['roles']
    if not isinstance(node, ast.Dict) or any(key is None for key in node.keys):
        raise ValueError('roles must be a literal mapping')
    pairs = [(ast.literal_eval(key), ast.literal_eval(value)) for key, value in zip(node.keys, node.values)]
    names = _names([key for key, _ in pairs], r'[A-Za-z][A-Za-z0-9_]*', 'role names')
    ids = [value for _, value in pairs]
    for value in ids:
        _names([value], r'C[0-9]+', 'Component ID')
    claim = {'roles': dict(zip(names, ids))}
    if 'entry_points' in args:
        claim['entry_points'] = _names(ast.literal_eval(args['entry_points']), r'[A-Za-z][A-Za-z0-9_]*', 'entry points')
    if 'current_record_count' in args:
        claim['current_record_count'] = _count(ast.literal_eval(args['current_record_count']))
    return claim


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError('current_record_count must be a nonnegative integer')
    return value


def group_to_mermaid(claim, component_id):
    _names([component_id], r'C[0-9]+', 'group Component ID')
    lines = ['flowchart TD', f'    {component_id}["{component_id}"]']
    lines += [f'    {component_id} -->|{role}| {child}["{child}"]'
              for role, child in claim['roles'].items()]
    return '\n'.join(lines)


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


def check_group_spec(root, component_id, manifest, contract, solution, *, structure_children, current_record_count=None, lean='lean'):
    """Compare pinned declarations with independently selected direct children."""
    from .boundary_model import load_boundary_model
    from .lean_spec__pub import compile_lean

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
                  mermaid=compiled['mermaid'], lean=compiled['lean'])
    return report
