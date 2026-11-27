"""Interpret formal boundary source claims and links."""
import ast

from ...LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SourceError, read_source as read_source


def require_link(carrier, relation, target, role=None, source=None):
    relations = carrier.metadata.get('relations', {})
    if not isinstance(relations, dict):
        raise SourceError(role, source, 'relations', 'expected a Header relations mapping')
    links = relations.get(relation)
    if not isinstance(links, list) or target not in links:
        raise SourceError(role, source, f'relations.{relation}', f'missing exact {relation} link to {target}')


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
        ('contract', 'python contract'): ('declare_contract', 'declare_http_contract', 'declare_tool_api_contract'),
        ('contract', 'python cli'): 'declare_cli_contract',
        ('contract', 'python trace'): 'declare_trace_contract',
        ('solution', 'python'): 'component_workflow',
        ('contract', 'python shape'): 'declare_shape_contract',
        ('contract', 'python framing'): 'declare_framing_contract',
        ('solution', 'python framing'): 'declare_framing_solution',
    }.get((role, language))
    if expected is None:
        return False
    constructors = (expected,) if isinstance(expected, str) else expected
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return False
    call = tree.body[0].value
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id in constructors)
