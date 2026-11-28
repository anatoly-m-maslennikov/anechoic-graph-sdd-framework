from __future__ import annotations

from types import MappingProxyType
from ....model.notation.subject_notation_types import (
    InitialAtomSelector,
    SubjectNotationError,
    SubjectProfile,
)
from ....model.notation.subject_notation_profiles import get_profile

_UNSUPPORTED_EXPRESSION_MARKERS = frozenset("\\[]{}&|?*")
_LEGACY_UNSUPPORTED_COMPONENT_MARKERS = frozenset("(),")
_UNSUPPORTED_SELECTOR_LITERAL_MARKERS = frozenset("\\[]{}&|?*@$")
_SELECTOR_KEYWORD = "atom"
_SELECTOR_ENTITY_TYPE_TERM = "Atom"


def parse_initial_atom_selector(
    component: str,
    *,
    subject_profile: str = "legacy",
) -> InitialAtomSelector | None:
    """Return one exact approved initial selector without resolving any Atom.

    The result preserves its complete selector literal and exposes the selected
    owner's existing Entity-type Term, ``Atom``.  It performs syntax validation
    only; callers must not treat it as a Term, a new Entity kind, or native
    endpoint admission.
    """

    profile = get_profile(subject_profile)
    if not isinstance(component, str):
        raise SubjectNotationError(
            "subject-invalid", "Subject component must be text"
        )
    literal = component.strip()
    if "@" in literal:
        raise SubjectNotationError(
            "subject-at-unsupported", "@ is not a Subject notation operator"
        )
    if profile.name != "approved":
        if _looks_like_selector(literal) or literal == _SELECTOR_KEYWORD:
            raise SubjectNotationError(
                "subject-form-unsupported",
                "Subject selectors are unsupported in the legacy profile",
            )
        return None
    return _parse_approved_selector(literal)


def _parse_approved_selector(literal):
    if literal == _SELECTOR_KEYWORD:
        raise SubjectNotationError(
            "subject-selector-invalid", "bare atom is not a Subject selector"
        )
    if literal.startswith(f"{_SELECTOR_KEYWORD}("):
        selector, end = _parse_selector_literal(literal)
        if end != len(literal):
            raise SubjectNotationError(
                "subject-selector-invalid",
                "selector must be one complete component",
            )
        return InitialAtomSelector(
            literal=literal,
            selector=MappingProxyType(selector),
            entity_type_term=_SELECTOR_ENTITY_TYPE_TERM,
        )
    if _looks_like_selector(literal):
        raise SubjectNotationError(
            "subject-selector-invalid",
            "Subject selector keyword must be exact lowercase atom",
        )
    return None


def parse_subject(
    value: str, *, subject_profile: str = "legacy"
) -> list[tuple[str, str | None]]:
    """Parse archived legacy syntax into its unchanged flat tuple contract.

    Approved expressions require the typed API because tuples cannot preserve
    grouping, qualification binding, or Relation cardinality slots.
    """

    profile = get_profile(subject_profile)
    if profile.name != "legacy":
        raise SubjectNotationError(
            "subject-flat-adapter-unsupported",
            (
                "approved Subjects require parse_subject_expression and its "
                "typed expression"
            ),
        )
    if not isinstance(value, str):
        raise SubjectNotationError("subject-invalid", "subject must be text")
    if "@" in value:
        raise SubjectNotationError(
            "subject-at-unsupported",
            "@ is not a legacy Subject notation operator",
        )
    if any(
        marker in value
        for marker in _UNSUPPORTED_EXPRESSION_MARKERS
        | _LEGACY_UNSUPPORTED_COMPONENT_MARKERS
    ):
        raise SubjectNotationError(
            "subject-form-unsupported", "unsupported legacy Subject form"
        )
    value = value.strip()
    if not value:
        raise SubjectNotationError(
            "subject-empty", "subject must contain one non-empty component"
        )
    return _split_subject_components(value, profile)


def _split_subject_components(
    value: str,
    profile: SubjectProfile,
    *,
    preceding_separator: str | None = None,
) -> list[tuple[str, str | None]]:
    """Split ordinary Subject components after selector handling, if any."""

    parsed: list[tuple[str, str | None]] = []
    component: list[str] = []
    position = 0
    while position < len(value):
        separator = _separator_at(value, position, profile)
        if separator is None:
            component.append(value[position])
            position += 1
            continue
        parsed.append(
            (_ordinary_component(component, profile), preceding_separator)
        )
        component.clear()
        preceding_separator = separator
        position += len(separator)

    parsed.append(
        (_ordinary_component(component, profile), preceding_separator)
    )
    return parsed


def _separator_at(
    value: str, position: int, profile: SubjectProfile
) -> str | None:
    """Return the longest registered separator beginning at one position."""

    return next(
        (
            separator
            for separator in profile.separators
            if value.startswith(separator, position)
        ),
        None,
    )


def _ordinary_component(component: list[str], profile: SubjectProfile) -> str:
    text = "".join(component).strip()
    if not text:
        raise SubjectNotationError(
            "subject-malformed",
            "Subject separators require non-empty components",
        )
    return text


def _parse_selector_literal(value: str) -> tuple[dict[str, str], int]:
    "Parse exactly one lowercase selector and return its map plus end index."

    position = len(_SELECTOR_KEYWORD) + 1
    selector: dict[str, str] = {}
    while True:
        position = _skip_whitespace(value, position)
        key_start = position
        while position < len(value) and (
            value[position].isalnum() or value[position] == "_"
        ):
            position += 1
        key = value[key_start:position]
        if not key:
            raise SubjectNotationError(
                "subject-selector-invalid", "selector requires a named key"
            )
        position = _skip_whitespace(value, position)
        if position >= len(value) or value[position] != "=":
            raise SubjectNotationError(
                "subject-selector-invalid",
                "selector key requires one quoted value",
            )
        position = _skip_whitespace(value, position + 1)
        literal, position = _selector_value(value, position)
        if key in selector:
            raise SubjectNotationError(
                "subject-selector-invalid", "selector keys must not repeat"
            )
        selector[key] = literal
        position = _skip_whitespace(value, position + 1)
        if position >= len(value):
            raise SubjectNotationError(
                "subject-selector-invalid", "selector is unterminated"
            )
        if value[position] == ")":
            position += 1
            break
        if value[position] != ",":
            raise SubjectNotationError(
                "subject-selector-invalid", "selector entries require commas"
            )
        position += 1

    return _validate_selector_keys(selector, position)


def _selector_value(value: str, position: int) -> tuple[str, int]:
    if position >= len(value) or value[position] != '"':
        raise SubjectNotationError(
            "subject-selector-invalid", "selector values must be double-quoted"
        )
    position += 1
    literal_start = position
    while position < len(value) and value[position] != '"':
        if value[position] == "\\":
            raise SubjectNotationError(
                "subject-selector-invalid", "selector escaping is unsupported"
            )
        position += 1
    if position >= len(value):
        raise SubjectNotationError(
            "subject-selector-invalid", "selector value is unterminated"
        )
    literal = value[literal_start:position]
    if not literal.strip() or any(
        ord(character) < 32 or ord(character) == 127 for character in literal
    ):
        raise SubjectNotationError(
            "subject-selector-invalid",
            "selector values must be non-empty printable literals",
        )
    if any(
        marker in literal for marker in _UNSUPPORTED_SELECTOR_LITERAL_MARKERS
    ):
        raise SubjectNotationError(
            "subject-selector-invalid",
            (
                "selector literals do not support escaping, wildcards, or "
                "expansion"
            ),
        )
    return literal, position


def _skip_whitespace(value: str, position: int) -> int:
    while position < len(value) and value[position].isspace():
        position += 1
    return position


def _looks_like_selector(value: str) -> bool:
    return value[:4].casefold() == _SELECTOR_KEYWORD and (
        value == _SELECTOR_KEYWORD or (len(value) > 4 and value[4] == "(")
    )


def _validate_selector_keys(selector, position):
    keys = tuple(selector)
    if keys == ("content_role",) or keys == ("content_role", "type"):
        return selector, position
    raise SubjectNotationError(
        "subject-selector-invalid",
        "selector must use content_role followed by optional type",
    )
