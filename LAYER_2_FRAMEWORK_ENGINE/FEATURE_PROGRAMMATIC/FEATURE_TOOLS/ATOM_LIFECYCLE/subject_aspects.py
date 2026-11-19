"""Resolve a Project Structure Aspect from its Current Declarations."""

import ast

import subject_notation as notation

from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from carrier_aliases import carrier_read_view, matches_named_value
from .source import query_reader, select_current_sources

_ASPECT_CLAIMS = (
    '"content.claim.formal_claim" ILIKE \'%aspect%\' '
    'AND ("content.claim.formal_claim" ILIKE \'%declare_entity%\' '
    'OR "content.claim.formal_claim" ILIKE \'%composition%\')'
)

def resolve_aspect(selection, expression, *, proposed_body=None):
    """Return whether a Current Declaration identifies this Aspect.

    ``None`` means the expression is outside this lookup's supported shape.
    An unavailable query reader is an explicit error.
    """
    target = _aspect_address(selection, expression, allow_named=True)
    if target is None:
        return None
    if proposed_body is not None and target in _declared_aspects(selection, proposed_body):
        return True
    reader = query_reader()
    if reader is None:
        raise ValueError("Aspect resolution requires the Project query API")
    references = declared_subject_candidates(reader, target[-1], _ASPECT_CLAIMS)
    pins = select_current_sources(selection, references)
    for pin in pins.values():
        view = carrier_read_view(pin.metadata)
        if (view.get("status", "").casefold() != "active"
                or not matches_named_value(view.get("role"), "Requirement")
                or not matches_named_value(view.get("form"), "Declaration")):
            continue
        body = parse_carrier(pin.raw, pin.path).body
        if target in _declared_aspects(selection, body):
            return True
    return False


def declared_subject_candidates(reader, name, claim_condition):
    literal = name.replace("'", "''")
    sql = (
        'SELECT DISTINCT reference FROM atoms WHERE status_group = \'Current\' '
        'AND position(lower(\'' + literal + "') in lower(\"content.claim.formal_claim\")) > 0 "
        f'AND ({claim_condition})'
    )
    result = reader.run(sql, page_size=1000, result_delivery="inline", result_format="json_matrix")
    if result.get("has_more") or not isinstance(result.get("rows"), list):
        raise ValueError("Subject Declaration query is incomplete")
    return sorted({row[0] for row in result["rows"] if isinstance(row, (list, tuple))
                   and len(row) == 1 and isinstance(row[0], str)})


def _declared_aspects(selection, body):
    result = set()
    for text in _native_block(body):
        if "composition(" in text:
            result.update(_composed_aspects(selection, text))
            continue
        if "declare_entity" not in text or not ("Aspect" in text or "aspect_memberships" in text):
            continue
        claim = parse_native_model_claim(text)
        if not claim or claim["kind"] != "entity":
            continue
        args = claim["arguments"]
        instance = args.get("instance", {})
        addresses = args.get("aspect_memberships", ())
        if instance.get("type") == "Aspect":
            addresses = (*addresses, instance.get("fields", {}).get("address"))
        for address in addresses:
            if isinstance(address, str) and (target := _aspect_address(selection, address)):
                result.add(target)
    return result


def _composed_aspects(selection, text):
    try:
        calls = _literal_calls(text, 'composition', {'container', 'parts'})
        expressions = [_composition_expression(call) for call in calls]
    except (SyntaxError, TypeError, ValueError):
        return ()
    return [target for expression in expressions
            if (target := _aspect_address(selection, expression, allow_named=True)) and target[0] == "Aspect"]


def _literal_calls(text, name, keys):
    calls = []
    for item in ast.parse(text, mode='exec').body:
        if not isinstance(item, ast.Expr) or not isinstance(item.value, ast.Call):
            raise ValueError('Expected a declarative call')
        call = item.value
        names = [keyword.arg for keyword in call.keywords]
        if (not isinstance(call.func, ast.Name) or call.func.id != name or call.args
                or len(names) != len(keys) or set(names) != keys):
            raise ValueError('Unsupported declarative call')
        calls.append({keyword.arg: ast.literal_eval(keyword.value) for keyword in call.keywords})
    if not calls:
        raise ValueError('Expected a declarative call')
    return calls


def _composition_expression(call):
    container, parts = call['container'], call['parts']
    if not isinstance(parts, tuple) or not parts:
        raise ValueError('Composition requires a nonempty tuple')
    endpoints, links = [], []
    for address in (container, *parts):
        if (not isinstance(address, str) or not address or address != address.strip()
                or any(ord(char) < 32 or ord(char) == 127 for char in address)):
            raise ValueError('Invalid composition address')
        expression = notation.parse_subject_expression(address, subject_profile='approved').expression
        if endpoints:
            links.append(notation.RelationLink('<+', None, None, None, notation.Span(0, 0)))
        if isinstance(expression, notation.RelationChain):
            endpoints.extend(expression.endpoints)
            links.extend(expression.links)
        else:
            endpoints.append(expression)
    return notation.RelationChain(tuple(endpoints), tuple(links), notation.Span(0, 0))


def _aspect_address(selection, expression, *, allow_named=False):
    if isinstance(expression, str):
        expression = notation.parse_subject_expression(expression, subject_profile="approved").expression
    if not isinstance(expression, notation.RelationChain):
        return None
    root, *parts = expression.endpoints
    if (isinstance(root.head, notation.Name) and root.head.value == "ANECHOIC" and not root.steps
            and isinstance(parts[0].head, notation.Name) and parts[0].head.value == "STRUCTURE"):
        if selection.settings["project"]["name"].casefold() != "anechoic":
            return None
        root, *parts = parts
    if any(link.operator != "<+" or link.relation_type is not None
           or link.forward_cardinality is not None or link.reverse_cardinality is not None
           for link in expression.links):
        return None
    project = selection.settings["project"]["name"]
    if not _project_root(root, project):
        return None
    if allow_named and len(parts) == 1 and (name := _named_aspect(parts[0])):
        return ("Aspect", name)
    if not all(isinstance(part.head, notation.Name) and not part.steps
               and part.value_format is None and part.value_cardinality is None for part in parts):
        return None
    if parts[0].head.value != "Aspects" or len(parts) < 2:
        return None
    return tuple(part.head.value for part in parts)


def _named_aspect(path):
    if (isinstance(path.head, notation.Name) and path.head.value == "Aspect" and len(path.steps) == 1
            and path.steps[0].operator == "//" and isinstance(path.steps[0].operand, notation.Name)
            and not path.value_format and not path.value_cardinality):
        return path.steps[0].operand.value


def _project_root(root, project):
    if not isinstance(root.head, notation.Name) or root.value_format or root.value_cardinality:
        return False
    if root.head.value == "ANECHOIC_STRUCTURE" and not root.steps:
        return project.casefold() == "anechoic"
    if root.head.value == "STRUCTURE" and not root.steps:
        return project.casefold() == "anechoic"
    return (root.head.value == "PROJECT STRUCTURE" and len(root.steps) == 1
            and root.steps[0].operator == "//" and isinstance(root.steps[0].operand, notation.Name)
            and root.steps[0].operand.value.casefold() == project.casefold())
