"""Select complete native Claims from an already-selected Declaration set."""

from collections.abc import Iterable, Mapping
from typing import Any

from markdown_it import MarkdownIt

import subject_notation as notation
from carrier_aliases import matches_named_value
from FEATURE_APPS.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content

from .native_model_claim import NativeModelClaimError, parse_native_model_claim


def _model_subject(subject: object, source: str) -> str | None:
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError(f"{source}: Declaration needs one Main Subject")
    try:
        expression = notation.parse_subject_expression(subject, subject_profile="approved").expression
    except notation.SubjectNotationError as error:
        raise ValueError(f"{source}: invalid Main Subject: {error}") from error
    if isinstance(expression, notation.RelationChain):
        first = expression.endpoints[0]
        if not (isinstance(first.head, notation.Name) and first.head.value == "CAPRMEDIO_MODEL"
                and not first.steps and expression.links[0].operator == "<+"
                and expression.links[0].relation_type is None):
            return None
    elif not (isinstance(expression.head, notation.Name)
              and expression.head.value == "CAPRMEDIO_MODEL" and not expression.steps):
        return None
    return notation.render_subject(expression)


def _native_claim(body: object, source: str) -> str:
    if not isinstance(body, str):
        raise ValueError(f"{source}: Declaration body is missing")
    try:
        records = parse_content(body)
    except ValueError as error:
        raise ValueError(f"{source}: invalid Markdown: {error}") from error
    sections = [record for record in records if record["property_path"] == ["claim", "formal_claim"]]
    if len(sections) != 1 or not isinstance(text := sections[0]["direct_markdown"], str):
        raise ValueError(f"{source}: expected one Formal Claim")
    tokens = MarkdownIt("commonmark").parse(text)
    if len(tokens) != 1 or tokens[0].type != "fence" or tokens[0].info.strip().casefold() != "python":
        raise ValueError(f"{source}: Formal Claim must contain one Python fence")
    token = tokens[0]
    last_line = text.splitlines()[token.map[1] - 1].strip()
    if len(last_line) < len(token.markup) or set(last_line) != {token.markup[0]}:
        raise ValueError(f"{source}: Python fence is not closed")
    try:
        declaration = parse_native_model_claim(token.content)
    except (NativeModelClaimError, SyntaxError, ValueError) as error:
        raise ValueError(f"{source}: invalid native Python Claim: {error}") from error
    if declaration is None:
        raise ValueError(f"{source}: Formal Claim is not a native Python Declaration")
    return token.content


def select_model_claims(carriers: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    """Read Current Requirement Declaration carriers under CAPRMEDIO_MODEL.

    The caller selects Declaration forms. Input records use the existing current
    carrier reader shape, including source, read_view, subjects and body.
    """
    claims, subjects, identifiers = [], {}, set()
    for carrier in carriers:
        source = carrier.get("source")
        if not isinstance(source, Mapping) or not isinstance(source.get("path"), str):
            raise ValueError("Declaration source path is missing")
        path = source["path"]
        view = carrier.get("read_view")
        if not isinstance(view, Mapping):
            raise ValueError(f"{path}: Declaration Header is missing")
        status = view.get("status")
        if not isinstance(status, str) or not status.strip():
            raise ValueError(f"{path}: Declaration Status is missing")
        if status.casefold() in {"draft", "archived", "backlog"}:
            continue
        if not matches_named_value(view.get("content_role"), "Requirement"):
            raise ValueError(f"{path}: selected Declaration must have Requirement Role")
        values = carrier.get("subjects")
        if not isinstance(values, Mapping):
            raise ValueError(f"{path}: Declaration Main Subject is missing")
        subject = _model_subject(values.get("active", values.get("governs")), path)
        if subject is None:
            continue
        identifier = source.get("atom_id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f"{path}: Declaration Atom ID is missing")
        if identifier in identifiers:
            raise ValueError(f"{path}: duplicate Current Declaration ID {identifier}")
        if subject in subjects:
            raise ValueError(f"{path}: duplicate Declaration Subject also in {subjects[subject]}")
        identifiers.add(identifier)
        subjects[subject] = path
        claims.append(_native_claim(carrier.get("body"), path))
    if not claims:
        raise ValueError("No Current CAPRMEDIO_MODEL Declarations were selected")
    return tuple(claims)
