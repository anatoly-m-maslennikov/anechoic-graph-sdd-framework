"""Match bounded CFEL expression forms."""

import json
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_blocks import _balanced_parentheses
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import _CONTROL, _count, _record, _sibling_order
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_expression_patterns import (
    _RELATION_ALIAS,
    _OPERATOR_SYMBOL,
    _COUNTERPART,
    _UNFILTERED_UNIQUE,
    _INSTANCE_BINDING,
    _SCOPED_INSTANCE_BINDING,
    _INSTANCE_POPULATION,
    _PROPERTY_INSTANCE_POPULATION,
    _MODEL_BINDING,
)


def _match_0(expression, group, operator, source, records, diagnostics):
    if group == "model" and operator and (symbol := _OPERATOR_SYMBOL.fullmatch(expression)):
        if symbol["name"] == operator["name"] and (value := json.loads(symbol["symbol"])):
            records.append(_record(source, expression, "operator_symbol", operator=symbol["name"], symbol=value))
            return True
    return False


def _match_1(expression, group, operator, source, records, diagnostics):
    uniqueness = _UNFILTERED_UNIQUE.fullmatch(expression) if group == "instances" else None
    if uniqueness is not None:
        records.append(_record(source, expression, "population_unique_constraint", group="instances",
                               population_selector=uniqueness.group("population").strip(),
                               keys=(uniqueness.group("key").strip(),)))
        return True
    return False


def _match_2(expression, group, operator, source, records, diagnostics):
    binder = _MODEL_BINDING.match(expression) if group == 'model' else None
    if binder is not None and expression.rstrip().endswith(')') and _balanced_parentheses(expression):
        records.append(_record(source, expression, "model_binding", variable=binder.group("variable"),
                               selection=binder.group("selection"), interpretation="opaque"))
        return True
    return False


def _match_3(expression, group, operator, source, records, diagnostics):
    population = _INSTANCE_POPULATION.fullmatch(expression) if group == 'instances' else None
    if population is not None:
        records.append(_record(source, expression, "instance_population_constraint",
                               kind_selector=population.group("kind").strip(), variable=population.group("variable"),
                               scope="project",
                               population_cardinality=_count(population.group("minimum"), population.group("tail"), population.group("maximum"))))
        return True
    return False


def _match_4(expression, group, operator, source, records, diagnostics):
    property_population = _PROPERTY_INSTANCE_POPULATION.fullmatch(expression)
    if property_population is not None:
        records.append(_record(source, expression, "property_instance_population_constraint",
                               bearer_selector=property_population.group("bearer").strip(),
                               property_selection="recursive_dependents", scope="per_bearer_each_schema",
                               population_cardinality=_count(property_population.group("minimum"), property_population.group("tail"), property_population.group("maximum"))))
        return True
    return False


def _match_5(expression, group, operator, source, records, diagnostics):
    binding = _INSTANCE_BINDING.fullmatch(expression) if group == 'instances' else None
    if binding is None and group == 'instances':
        scoped_binding = _SCOPED_INSTANCE_BINDING.fullmatch(expression)
        if scoped_binding is not None:
            try:
                kind = notation.parse_subject_expression(scoped_binding.group("kind"), subject_profile="approved").expression
            except notation.SubjectNotationError:
                kind = None
            if (isinstance(kind, notation.Path) and isinstance(kind.head, notation.Name)
                    and kind.value_format is None and kind.value_cardinality is None
                    and any(isinstance(step.operand, notation.Qualification) for step in kind.steps)
                    and all(step.operator in {"/", "."} and isinstance(step.operand, (notation.Name, notation.Qualification)) for step in kind.steps)):
                binding = scoped_binding
    if binding is not None:
        records.append(_record(source, expression, "instance_binding", kind_selector=binding.group("kind").strip(), variable=binding.group("variable")))
        return True
    return False


def _match_6(expression, group, operator, source, records, diagnostics):
    alias = _RELATION_ALIAS.fullmatch(expression)
    if alias is not None:
        records.append(_record(source, expression, "relation_alias", relation=alias.group("name"), glyph=alias.group("glyph")))
        return True
    return False


def _match_7(expression, group, operator, source, records, diagnostics):
    counterpart = _COUNTERPART.fullmatch(expression)
    if counterpart is not None:
        records.append(_record(source, expression, "relation_cardinality", source_selector=counterpart.group("source"),
                               relation="HAS_INVERSE", relation_notation="<-->", target_selector=counterpart.group("target"),
                               source_cardinality=None, target_cardinality=None, written_direction="forward"))
        return True
    return False


def _match_8(expression, group, operator, source, records, diagnostics):
    if _CONTROL.search(expression):
        diagnostics.append({
            "code": "cfel-expression-unsupported",
            "message": "CFEL control expression is outside the bounded projection extractor.",
            "expression": expression,
            "source": dict(source),
        })
        return True
    return False


def _match_9(expression, group, operator, source, records, diagnostics):
    if order := _sibling_order(expression):
        records.append(_record(source, expression, "relation_cardinality", **order))
        return True
    return False

MATCHERS = (_match_0, _match_1, _match_2, _match_3, _match_4, _match_5, _match_6, _match_7, _match_8, _match_9,)
