"""Select complete native Claims from an already-selected Declaration set."""

from collections.abc import Iterable, Mapping
from functools import cache
from typing import Any
from markdown_it import MarkdownIt
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    matches_named_value,
)
from ....FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared import (
        lint_native_model_claim,
        resolve_model_claim_reference,
    )  # fmt: skip
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    canonical_model_address,
    model_class_target,
    model_declaration_subject,
    simple_model_address,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_content,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NativeModelClaimError,
    parse_native_model_claim,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.dataclass_field_contract__pub import (
    validate_field_contracts,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    order_properties,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.relation_declaration_catalog__pub import (
    build_relation_declaration_catalog,
)
from .model_property_aliases import (
    class_property_aliases as _class_property_aliases,
)
from .model_constraint_claims import _merge_constraint_claims

from .model_declaration_checks import (
    _add_unambiguous_addresses as _add_unambiguous_addresses,
    _check_node_axes as _check_node_axes,
    relation_axis_values as relation_axis_values,
    _check_constraint_endpoints,
    _check_manifest_property_bearers,
    _check_relation_axes,
)


def _native_claim(body: object, source: str, subject: str) -> str:
    if not isinstance(body, str):
        raise ValueError(f"{source}: Declaration body is missing")
    try:
        records = parse_content(body)
    except ValueError as error:
        raise ValueError(f"{source}: invalid Markdown: {error}") from error
    sections = [
        record
        for record in records
        if record["property_path"] == ["claim", "formal_claim"]
    ]
    if len(sections) != 1 or not isinstance(
        text := sections[0]["direct_markdown"], str
    ):
        raise ValueError(f"{source}: expected one Formal Claim")
    return _native_claim_text(text, source, subject)


def _native_claim_text(text: str, source: str, subject: str) -> str:
    tokens = MarkdownIt("commonmark").parse(text)
    if (
        len(tokens) != 1
        or tokens[0].type != "fence"
        or tokens[0].info.strip().casefold() != "python"
    ):
        raise ValueError(
            f"{source}: Formal Claim must contain one Python fence"
        )
    token = tokens[0]
    last_line = text.splitlines()[token.map[1] - 1].strip()
    if len(last_line) < len(token.markup) or set(last_line) != {
        token.markup[0]
    }:
        raise ValueError(f"{source}: Python fence is not closed")
    try:
        declaration = parse_native_model_claim(token.content)
    except (NativeModelClaimError, SyntaxError, ValueError) as error:
        raise ValueError(
            f"{source}: invalid native Python Claim: {error}"
        ) from error
    if declaration is None:
        raise ValueError(
            f"{source}: Formal Claim is not a native Python Declaration"
        )
    arguments = declaration["arguments"]
    if (
        "entity_class" in arguments
        and model_class_target(subject, arguments["entity_name"]) is None
    ):
        raise ValueError(
            f"{source}: declared class does not match its Main Subject"
        )
    if pairs := arguments.get("ordered_dependent_property_pairs"):
        try:
            order_properties((), pairs)
        except ValueError as error:
            raise ValueError(f"{source}: {error}") from error
    return token.content


def _check_relation_references(records: list[tuple[str, str, str]]) -> None:
    """Build the Relation registry and check references."""
    parsed = _merge_constraint_claims(
        [
            (source, subject, parse_native_model_claim(claim))
            for source, subject, claim in records
        ]
    )
    _check_manifest_property_bearers(parsed)
    relations = build_relation_declaration_catalog(parsed)
    explicit = {
        name
        for name, (args, reverse) in relations.items()
        if not reverse and "derived_from" not in args
    }
    for source, _, declaration in parsed:
        names = declaration["arguments"].get("allowed_relation_names")
        if names is not None and set(names) != explicit:
            raise ValueError(
                f"{source}: allowed Relation names must match "
                "the explicit Model catalog"
            )
    _check_relation_axes(parsed, relations)
    addresses = {subject for _, subject, _ in records}
    addresses.update(_class_property_aliases(parsed))
    _add_unambiguous_addresses(addresses, parsed)
    _lint_relation_references(parsed, addresses, relations)
    _check_constraint_endpoints(parsed, relations)


def select_model_declarations(
    carriers: Iterable[Mapping[str, Any]],
) -> tuple[tuple[str, str, str], ...]:
    """Read Current Requirement Declaration carriers under ANECHOIC_MODEL.

    The caller selects Declaration forms. Input records use the current
    carrier reader shape, including source, read_view, subjects and body.
    """
    subjects, identifiers, records = {}, set(), []
    for carrier in carriers:
        selected = _selected_carrier(carrier)
        if selected is None:
            continue
        source, path, subject = selected
        identifier = source.get("atom_id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{path}: Declaration Atom ID is missing")
        if identifier in identifiers:
            raise ValueError(
                f"{path}: duplicate Current Declaration ID {identifier}"
            )
        if subject in subjects:
            raise ValueError(
                f"{path}: duplicate Declaration Subject also in "
                f"{subjects[subject]}"
            )
        identifiers.add(identifier)
        subjects[subject] = path
        claim = _native_claim(carrier.get("body"), path, subject)
        records.append((path, subject, claim))
    if not records:
        raise ValueError(
            "No Current ANECHOIC_MODEL Declarations were selected"
        )
    _check_relation_references(records)
    return tuple(records)


def select_model_claims(
    carriers: Iterable[Mapping[str, Any]],
) -> tuple[str, ...]:
    return tuple(claim for _, _, claim in select_model_declarations(carriers))


def _selected_carrier(carrier):
    source = carrier.get("source")
    if not isinstance(source, Mapping) or not isinstance(
        source.get("path"), str
    ):
        raise ValueError("Declaration source path is missing")
    path = source["path"]
    view = carrier.get("read_view")
    if not isinstance(view, Mapping):
        raise ValueError(f"{path}: Declaration Header is missing")
    status = view.get("status")
    if not isinstance(status, str) or not status.strip():
        raise ValueError(f"{path}: Declaration Status is missing")
    if status.casefold() in {"draft", "archived", "backlog"}:
        return None
    if not matches_named_value(view.get("content_role"), "Requirement"):
        raise ValueError(
            f"{path}: selected Declaration must have Requirement Role"
        )
    values = carrier.get("subjects")
    if not isinstance(values, Mapping):
        raise ValueError(f"{path}: Declaration Main Subject is missing")
    subject = model_declaration_subject(
        values.get("active", values.get("governs")), path
    )
    if subject is None:
        return None
    return source, path, subject


def _lint_relation_references(parsed, addresses, relations):
    simple_address = cache(simple_model_address)
    canonical_address = cache(canonical_model_address)
    keys = {
        "source_endpoint",
        "target_endpoint",
        "endpoint_pairs",
        "relation_name",
        "incoming_model_relations",
        "model_relation_constraints",
        "instance_relation_constraints",
        "population_unique_constraints",
        "population_entity_path",
        "base_path",
        "entity_name",
    }
    for source, subject, declaration in sorted(
        parsed, key=lambda item: item[2]["kind"] != "relation"
    ):
        _lint_relation(
            source,
            subject,
            declaration,
            keys,
            addresses,
            relations,
            simple_address,
            canonical_address,
        )


def _lint_relation(
    source,
    subject,
    declaration,
    keys,
    addresses,
    relations,
    simple_address,
    canonical_address,
):
    try:
        validate_field_contracts(declaration)
    except ValueError as error:
        raise ValueError(
            f"{source}:{declaration['line']}:1: {error}"
        ) from error
    arguments = _relation_arguments(declaration, subject, keys)
    check = {
        **declaration,
        "arguments": arguments,
        "imports": {},
        "classes": (),
    }
    check.pop("instance_check", None)
    errors = lint_native_model_claim(
        check,
        declared_addresses=addresses,
        relation_names=set(relations),
        path=source,
        first_line=1,
        resolve_address=resolve_model_claim_reference,
        simple_address=simple_address,
        canonical_address=canonical_address,
    )
    if errors:
        raise ValueError(errors[0])


def _relation_arguments(declaration, subject, keys):
    arguments = {
        key: value
        for key, value in declaration["arguments"].items()
        if key in keys
    }
    if (
        "population_unique_constraints" in arguments
        and "entity_class" in declaration["arguments"]
    ):
        arguments.setdefault(
            "population_entity_path",
            model_class_target(subject, arguments["entity_name"]),
        )
    if declaration["kind"] == "relation":
        arguments.pop("relation_name", None)
    return arguments
