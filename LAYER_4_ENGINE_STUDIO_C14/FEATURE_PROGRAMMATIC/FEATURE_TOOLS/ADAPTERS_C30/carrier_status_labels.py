"""Read and normalize Carrier Status labels."""

import re
from typing import Any


def carrier_status_folder(name: str) -> str:
    """Read the semantic label of an ordinary or three-digit Status folder."""
    label = re.sub(r"^[0-9]{3}_", "", name.casefold())
    return {"drafts": "draft", "archive": "archived"}.get(label, label)


def named_value_token(canonical: str) -> str | None:
    if not isinstance(canonical, str) or not re.fullmatch(
        r"[A-Za-z0-9]+(?:[ _-]+[A-Za-z0-9]+)*", canonical
    ):
        return None
    return re.sub(r"[ _-]+", "_", canonical).lower()


def matches_named_value(carried: Any, canonical: str) -> bool:
    token = named_value_token(canonical)
    return carried == canonical or (token is not None and carried == token)


class StatusModelError(ValueError):
    """A source or compiled Status model is invalid or unsupported."""


def _encode_status(value: str) -> str:
    token = named_value_token(value)
    if token is None:
        raise StatusModelError("Unsupported Status name encoding")
    return token


def canonical_status(model: Any, role: str, form: str, carried: object) -> str:
    allowed: frozenset[str] = model.allowed(role, form)
    encoded: dict[str, str] = {}
    for value in allowed:
        key = _encode_status(value)
        if key in encoded and encoded[key] != value:
            raise StatusModelError("Ambiguous Status encoding")
        encoded[key] = value
    matches = {
        value for value in allowed if matches_named_value(carried, value)
    }
    if len(matches) != 1:
        raise StatusModelError(
            "Status is not admitted by the applicable model"
        )
    return matches.pop()
