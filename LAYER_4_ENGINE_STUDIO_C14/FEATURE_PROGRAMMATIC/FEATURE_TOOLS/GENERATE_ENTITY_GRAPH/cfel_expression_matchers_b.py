"""Match bounded CFEL expression forms."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_blocks import _balanced_parentheses
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import _count, _named_property_count, _property_selector, _record
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_expression_patterns import (
    _PROPERTY,
    _PROPERTY_VALUE,
    _NAMED_PROPERTY,
    _RELATION,
    _GROUPED_INSTANCE_RELATION,
    _RELATION_WITHOUT_TARGET,
    _ALLOWED_CLASSIFICATION_VALUE,
    _FORWARD_CLASSIFICATION,
    _REVERSE_CLASSIFICATION,
    _FORWARD_GROUPED_CLASSIFICATION,
    _REVERSE_GROUPED_CLASSIFICATION,
    _ALLOWED_LITERAL,
    _QUALIFIED_ALLOWED_LITERAL,
    _PROPERTY_MINIMUM,
)


def _match_10(expression, group, operator, source, records, diagnostics):
    grouped_instance = _GROUPED_INSTANCE_RELATION.fullmatch(expression)
    if grouped_instance is not None:
        try:
            grouped = _subject_parse_subject_expression(grouped_instance.group("source"), subject_profile="approved").expression
            target = _subject_parse_subject_expression(grouped_instance.group("target").strip(), subject_profile="approved").expression
        except _subject_SubjectNotationError:
            grouped = target = None
        if (isinstance(grouped, _subject_RelationChain) and grouped.links
                and all(link.operator == "<+" and link.relation_type is None
                        and link.forward_cardinality is None and link.reverse_cardinality is None
                        for link in grouped.links)
                and all(isinstance(endpoint.head, _subject_Name) and not endpoint.value_format
                        and not endpoint.value_cardinality and all(
                            step.operator in {"/", "//"} and isinstance(step.operand, _subject_Name)
                            for step in endpoint.steps) for endpoint in grouped.endpoints)
                and isinstance(target, _subject_Path) and isinstance(target.head, _subject_Name)
                and not target.steps and target.value_format is None and target.value_cardinality is None):
            written_source = "(" + grouped_instance.group("source").strip() + ")"
            written_target = grouped_instance.group("target").strip()
            records.append(_record(
                source, expression, "relation_cardinality", source_selector=written_source,
                relation="IS_INSTANCE_OF", relation_notation=None, target_selector=written_target,
                source_cardinality=None, target_cardinality=None, written_direction="forward",
                written_source_selector=written_source, written_target_selector=written_target,
                written_source_cardinality=None, written_target_cardinality=None,
            ))
            return True
    return False


def _match_11(expression, group, operator, source, records, diagnostics):
    relation = _RELATION.fullmatch(expression)
    if relation is not None and _balanced_parentheses(relation.group("source")) and _balanced_parentheses(relation.group("target")) and not (relation.group("source").rstrip().endswith(":")
                                     or relation.group("target").lstrip().startswith(":")):
        reverse_named = relation.group("reverse_relation") is not None
        written_source = relation.group("source").strip()
        written_target = relation.group("target").strip()
        written_forward = _count(
            relation.group("forward_minimum"), relation.group("forward_tail"), relation.group("forward_maximum"),
        )
        written_reverse = _count(
            relation.group("reverse_minimum"), relation.group("reverse_tail"), relation.group("reverse_maximum"),
        )
        records.append(_record(
            source, expression, "relation_cardinality",
            source_selector=written_target if reverse_named else written_source,
            relation=(relation.group("reverse_relation") or relation.group("relation")).strip()
            if (relation.group("reverse_relation") or relation.group("relation")) else None,
            relation_notation=relation.group("relation_notation"),
            target_selector=written_source if reverse_named else written_target,
            source_cardinality=written_reverse if reverse_named else written_forward,
            target_cardinality=written_forward if reverse_named else written_reverse,
            written_direction="reverse" if reverse_named else "forward",
            written_source_selector=written_source,
            written_target_selector=written_target,
            written_source_cardinality=written_forward,
            written_target_cardinality=written_reverse,
        ))
        return True
    return False


def _match_12(expression, group, operator, source, records, diagnostics):
    relation_without_target = _RELATION_WITHOUT_TARGET.fullmatch(expression)
    if relation_without_target is not None:
        relation_name = (
            relation_without_target.group("relation")
            or relation_without_target.group("bare_relation")
        )
        records.append(_record(
            source, expression, "relation_cardinality",
            source_selector=relation_without_target.group("source").strip(),
            relation=relation_name,
            relation_notation=relation_without_target.group("relation_notation"),
            target_selector=None,
            source_cardinality=_count(
                relation_without_target.group("forward_minimum"),
                relation_without_target.group("forward_tail"),
                relation_without_target.group("forward_maximum"),
            ),
            target_cardinality=None,
            selection="all_relations" if relation_name == "*" else "named_relation",
            written_direction="forward",
            target_domain="unresolved",
        ))
        return True
    return False


def _match_13(expression, group, operator, source, records, diagnostics):
    allowed_classification = _ALLOWED_CLASSIFICATION_VALUE.fullmatch(expression)
    if allowed_classification is not None:
        records.append(_record(source, expression, "classification_allowed_value",
                               subject_selector=allowed_classification.group("subject").strip(),
                               axis=allowed_classification.group("axis").strip(),
                               value=allowed_classification.group("value").strip()))
        return True
    return False


def _match_14(expression, group, operator, source, records, diagnostics):
    classification = (
        _FORWARD_GROUPED_CLASSIFICATION.fullmatch(expression)
        or _REVERSE_GROUPED_CLASSIFICATION.fullmatch(expression)
        or _FORWARD_CLASSIFICATION.fullmatch(expression)
        or _REVERSE_CLASSIFICATION.fullmatch(expression)
    )
    if classification is not None:
        records.append(_record(
            source, expression, "classification_condition",
            subject_selector=classification.group("subject").strip(),
            axis=classification.group("axis").strip(),
            operator=classification.group("operator"),
            value=classification.group("value").strip(),
        ))
        return True
    return False


def _match_15(expression, group, operator, source, records, diagnostics):
    named_property = _NAMED_PROPERTY.fullmatch(expression)
    named_selector = _property_selector(named_property.group("property")) if named_property is not None else None
    if named_property is not None and named_selector is not None:
        occurrence = _count(named_property.group("minimum"), named_property.group("tail"), named_property.group("maximum"))
        effective = _named_property_count(occurrence)
        records.append(_record(source, expression, "property_constraint", property_selector=named_selector,
                               selection="property", name_format=None, occurrence_cardinality=occurrence,
                               effective_occurrence_cardinality=effective, occurrence_conflict=effective is None,
                               value_format=None, value_cardinality=None))
        return True
    return False


def _match_16(expression, group, operator, source, records, diagnostics):
    property_constraint = _PROPERTY.fullmatch(expression)
    property_selector = _property_selector(property_constraint.group("property")) if property_constraint is not None else None
    if property_constraint is not None and property_selector is not None and not (
        property_constraint.group("descendants") is None
        and property_constraint.group("property").rstrip().endswith(":")
    ):
        selection = {None: "property", ".*": "immediate_dependents", ".**": "recursive_dependents"}[
            property_constraint.group("descendants")
        ]
        occurrence = _count(property_constraint.group("minimum"), property_constraint.group("tail"), property_constraint.group("maximum"))
        named = selection == "property" and property_constraint.group("name_format") is None
        value_count = _count(property_constraint.group("value_minimum"), property_constraint.group("value_tail"), property_constraint.group("value_maximum"))
        effective = _named_property_count(occurrence, value_count) if named else occurrence
        records.append(_record(
            source, expression, "property_constraint",
            property_selector=property_selector,
            selection=selection,
            name_format=property_constraint.group("name_format"),
            occurrence_cardinality=occurrence,
            effective_occurrence_cardinality=effective,
            occurrence_conflict=named and effective is None,
            value_format=property_constraint.group("value_format"),
            value_cardinality=value_count,
        ))
        return True
    return False


def _match_17(expression, group, operator, source, records, diagnostics):
    property_value = _PROPERTY_VALUE.fullmatch(expression)
    value_selector = _property_selector(property_value.group("property")) if property_value is not None else None
    if (property_value is not None and value_selector is not None
            and (property_value.group("value_format") is not None or property_value.group("minimum") is not None)):
        value_count = _count(property_value.group("minimum"), property_value.group("tail"), property_value.group("maximum"))
        descendants = property_value.group("descendants")
        records.append(_record(
            source, expression, "property_constraint",
            property_selector=value_selector,
            selection={None: "values", ".*": "immediate_dependent_values", ".**": "recursive_dependent_values"}[descendants],
            name_format=None,
            occurrence_cardinality=None,
            **({"effective_occurrence_cardinality": _named_property_count(None, value_count)} if descendants is None else {}),
            value_format=property_value.group("value_format"),
            value_cardinality=value_count,
        ))
        return True
    return False


def _match_18(expression, group, operator, source, records, diagnostics):
    minimum = _PROPERTY_MINIMUM.fullmatch(expression)
    if minimum is not None and (minimum_selector := _property_selector(minimum["property"])):
        written_value = minimum["value"]
        value = float(written_value) if "." in written_value else int(written_value)
        records.append(_record(source, expression, "property_value_bound",
                               property_selector=minimum_selector, operator=">=", value=value))
        return True
    return False


def _match_19(expression, group, operator, source, records, diagnostics):
    allowed_literal = _ALLOWED_LITERAL.fullmatch(expression)
    literal_selector = _property_selector(allowed_literal.group("property")) if allowed_literal is not None else None
    if literal_selector is None:
        allowed_literal = _QUALIFIED_ALLOWED_LITERAL.fullmatch(expression)
        literal_selector = _property_selector(allowed_literal.group("property")) if allowed_literal is not None else None
    if allowed_literal is not None and literal_selector is not None and not any(
        token in expression for token in (":=", ": =", "'", '"', ">|", "|<", "((")
    ) and not any(token in allowed_literal.group("literal") for token in ("(", ")")):
        records.append(_record(
            source, expression, "allowed_literal",
            property_selector=literal_selector,
            literal=allowed_literal.group("literal").strip(),
        ))
        return True
    return False


def _match_20(expression, group, operator, source, records, diagnostics):
    if group in {None, "model"}:
        try:
            subject = _subject_parse_subject_expression(expression, subject_profile="approved").expression
        except _subject_SubjectNotationError:
            subject = None
        if (isinstance(subject, _subject_Path) and isinstance(subject.head, _subject_Name)
                and subject.value_format is None and subject.value_cardinality is None
                and all(step.operator in {"/", "."} and isinstance(step.operand, (_subject_Name, _subject_Qualification)) for step in subject.steps)):
            records.append(_record(source, expression, "subject_expression", selector=_subject_render_subject(subject)))
            return True
    return False

MATCHERS = (_match_10, _match_11, _match_12, _match_13, _match_14, _match_15, _match_16, _match_17, _match_18, _match_19, _match_20,)
