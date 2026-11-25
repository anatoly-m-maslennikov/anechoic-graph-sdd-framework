"""Parse and compare a bounded record and subtype without executing Python."""

import ast
import re

from .top_down__pub import compare_obligations


def _name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', value):
        raise ValueError('shape names must be simple ASCII identifiers')
    return value


def parse_shape(source, role):
    tree = ast.parse(source)
    if role == 'contract':
        return _parse_contract(tree)
    return _parse_solution(tree, role)


def _parse_contract(tree):
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        raise ValueError('expected one shape contract')
    call = tree.body[0].value
    if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name)
            or call.func.id != 'declare_shape_contract' or call.args
            or len(call.keywords) != 3 or {k.arg for k in call.keywords} != {'record', 'fields', 'subtype'}):
        raise ValueError('expected record, fields and subtype')
    args = {k.arg: k.value for k in call.keywords}
    fields_node = args['fields']
    if not isinstance(fields_node, ast.Dict) or not fields_node.keys:
        raise ValueError('expected nonempty literal fields')
    pairs = [(ast.literal_eval(k), ast.literal_eval(v)) for k, v in zip(fields_node.keys, fields_node.values)]
    fields = {_name(k): _name(v) for k, v in pairs}
    if len(fields) != len(pairs):
        raise ValueError('duplicate field')
    record, subtype = _name(ast.literal_eval(args['record'])), _name(ast.literal_eval(args['subtype']))
    if record == subtype or {record, subtype} & set(fields.values()):
        raise ValueError('record, subtype and field types must be distinct')
    return {'record': record, 'fields': fields, 'subtype': subtype, 'base': record}


def _parse_solution(tree, role):
    if role != 'solution' or len(tree.body) != 2 or any(not isinstance(c, ast.ClassDef) for c in tree.body):
        raise ValueError('expected one record and one subtype class')
    record, subtype = tree.body
    if (record.name == subtype.name or record.bases or record.keywords or record.decorator_list
            or subtype.keywords or subtype.decorator_list or len(subtype.bases) > 1
            or any(not isinstance(base, ast.Name) for base in subtype.bases)
            or len(subtype.body) != 1 or not isinstance(subtype.body[0], ast.Pass)):
        raise ValueError('unsupported shape class syntax')
    fields = {}
    for field in record.body:
        if isinstance(field, ast.Pass) and len(record.body) == 1:
            continue
        if (not isinstance(field, ast.AnnAssign) or not isinstance(field.target, ast.Name)
                or not isinstance(field.annotation, ast.Name) or field.value is not None or not field.simple):
            raise ValueError('record fields must be typed names without values')
        name = _name(field.target.id)
        if name in fields:
            raise ValueError('duplicate field')
        fields[name] = _name(field.annotation.id)
    base = _name(subtype.bases[0].id) if subtype.bases else None
    if base not in (None, record.name):
        raise ValueError('subtype base must be the record')
    if {record.name, subtype.name} & set(fields.values()):
        raise ValueError('record, subtype and field types must be distinct')
    return {'record': _name(record.name), 'fields': fields, 'subtype': _name(subtype.name), 'base': base}


def _quoted(name):
    return '«' + name + '»'


def shape_to_lean(claim, role):
    q = _quoted
    types = sorted(set(claim['fields'].values()))
    params = ''.join(f' ({q(t)} : Type)' for t in types)
    args = ''.join(f' {q(t)}' for t in types)
    lines = [f'namespace Shape_{role}', f'structure {q(claim["record"])}{params} where']
    lines += [f'  {q(name)} : {q(typ)}' for name, typ in claim['fields'].items()]
    if claim['base'] == claim['record']:
        lines.append(f'structure {q(claim["subtype"])}{params} extends {q(claim["record"])}{args} where')
    else:
        lines.append(f'structure {q(claim["subtype"])} where')
    lines.append(f'end Shape_{role}')
    return '\n'.join(lines)


def shape_to_mermaid(claim):
    lines = ['classDiagram', f'    class {claim["record"]} {{']
    lines += [f'        {typ} {name}' for name, typ in claim['fields'].items()]
    lines += ['    }', f'    class {claim["subtype"]}']
    if claim['base']:
        lines.append(f'    {claim["base"]} <|-- {claim["subtype"]}')
    return '\n'.join(lines)


def check_shape_spec(root, component_id, manifest, contract, solution, *, lean='lean'):
    """Compare the pinned Contract against the observed Solution shape."""
    from .boundary_model import load_boundary_model
    from .lean_spec__pub import compile_lean

    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    claims = compiled['claims']
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
    report.update(issues=compiled['issues'], unresolved=compiled['unresolved'], mermaid=compiled['mermaid'], lean=compiled['lean'])
    return report
