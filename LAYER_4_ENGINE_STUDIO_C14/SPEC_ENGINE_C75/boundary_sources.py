"""Read and pin formal boundary carriers without executing their source."""
import ast
import hashlib
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_carrier,
)


def read_source(root, pin, role):
    required = {'path', 'atom_id', 'version', 'status', 'container_component'}
    if (set(pin) != required or type(pin['version']) is not int or pin['version'] < 1
            or pin['status'] not in {'active', 'draft', 'ready'}
            or any(not isinstance(pin[key], str) or not pin[key]
                   for key in ('path', 'atom_id', 'container_component'))):
        raise ValueError(f'invalid {role} source pin')
    root = Path(root).resolve()
    path = (root / pin['path']).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f'invalid {role} source path')
    raw = path.read_bytes()
    carrier = parse_carrier(raw, path)
    meta = carrier.metadata
    if (meta.get('atom_family') != 'SPEC' or meta.get('atom_id') != pin['atom_id']
            or meta.get('container', {}).get('component') != pin['container_component']
            or meta.get('state', {}).get('version') != pin['version']
            or type(meta.get('state', {}).get('version')) is not int
            or meta.get('state', {}).get('status') != pin['status']):
        raise ValueError(f'{role} does not match source pin')
    return carrier, {**pin, 'sha256': hashlib.sha256(raw).hexdigest()}


def require_link(carrier, relation, target):
    links = carrier.metadata.get('relations', {}).get(relation)
    if not isinstance(links, list) or target not in links:
        raise ValueError(f'missing exact {relation} link to {target}')


def recognized_claim(role, language, source):
    """Recognize a form only; downstream parsers validate its contents."""
    if language == 'python shape' and role == 'solution':
        try:
            body = ast.parse(source).body
            return len(body) == 2 and all(isinstance(node, ast.ClassDef) for node in body)
        except SyntaxError:
            return False
    if language == 'lean':
        return True
    expected = {
        ('contract', 'python group'): 'declare_group_contract',
        ('solution', 'python group'): 'component_group',
        ('contract', 'python contract'): 'declare_contract',
        ('contract', 'python cli'): 'declare_cli_contract',
        ('contract', 'python trace'): 'declare_trace_contract',
        ('solution', 'python'): 'component_workflow',
        ('contract', 'python shape'): 'declare_shape_contract',
        ('contract', 'python framing'): 'declare_framing_contract',
        ('solution', 'python framing'): 'declare_framing_solution',
    }.get((role, language))
    if expected is None:
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return False
    call = tree.body[0].value
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == expected)
