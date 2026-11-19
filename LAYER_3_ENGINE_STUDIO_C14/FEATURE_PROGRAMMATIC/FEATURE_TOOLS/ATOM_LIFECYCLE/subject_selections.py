"""Resolve named Selections from their Current defining Claims."""

import subject_notation as notation

from carrier_aliases import carrier_read_view, matches_named_value
from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
from header_groups import header_value
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from .source import query_reader, select_current_sources
from .subject_aspects import _literal_calls, declared_subject_candidates


def resolve_named_selection(selection, subject):
    local = notation.namespace_local_expression(subject) or subject
    if not (isinstance(local, notation.Path) and isinstance(local.head, notation.Name)
            and local.head.value == "Named Selection" and len(local.steps) == 1
            and local.steps[0].operator == "//" and isinstance(local.steps[0].operand, notation.Name)
            and not local.value_format and not local.value_cardinality):
        return None
    project = selection.settings["project"]["name"]
    if isinstance(subject, notation.RelationChain):
        root = subject.endpoints[0]
        if isinstance(root.head, notation.Name) and root.head.value == "PROJECT STRUCTURE" and (
            len(root.steps) != 1 or not isinstance(root.steps[0].operand, notation.Name)
            or root.steps[0].operand.value.casefold() != project.casefold()
        ):
            return False
    reader = query_reader()
    if reader is None:
        raise ValueError("Named Selection resolution requires the Project query API")
    refs = declared_subject_candidates(reader, local.steps[0].operand.value,
                                      '"content.claim.formal_claim" ILIKE \'%subject_path%\'')
    target = notation.render_subject(local)
    matches = [pin for pin in select_current_sources(selection, refs).values() if _defines_selection(pin, target)]
    if len(matches) > 1:
        raise ValueError("Named Selection has ambiguous Current defining Claims")
    return bool(matches)


def _defines_selection(pin, target):
    view = carrier_read_view(pin.metadata)
    if (not matches_named_value(view.get("role"), "Requirement")
            or not matches_named_value(view.get("status"), "Active")
            or not any(matches_named_value(view.get("form"), form) for form in ("Rule", "Requirement", "Declaration"))):
        return False
    _, address = header_value(pin.metadata, "topics.main_subject")
    if not isinstance(address, str) or _local_address(address) != target:
        return False
    body = parse_carrier(pin.raw, pin.path).body
    for text in _native_block(body):
        try:
            calls = _literal_calls(text, 'subject_path', {'address'})
        except (SyntaxError, TypeError, ValueError):
            continue
        if len(calls) == 1 and calls[0]['address'] == target:
            return True
    return False


def _local_address(address):
    expression = notation.parse_subject_expression(address, subject_profile="approved").expression
    return notation.render_subject(notation.namespace_local_expression(expression) or expression)
