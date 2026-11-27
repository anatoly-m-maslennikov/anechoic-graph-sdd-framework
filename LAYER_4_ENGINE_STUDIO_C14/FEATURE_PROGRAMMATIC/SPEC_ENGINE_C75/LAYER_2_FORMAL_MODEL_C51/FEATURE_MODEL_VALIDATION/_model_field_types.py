"""Check that validation preserves field value types."""

from collections.abc import Mapping


def _same_types(original, validated):
    if type(original) is not type(validated):
        return False
    if isinstance(original, Mapping):
        return all(
            _same_types(key, new_key)
            and _same_types(value, validated[new_key])
            for (key, value), new_key in zip(
                original.items(), validated, strict=True
            )
        )
    if isinstance(original, (list, tuple)):
        return all(
            _same_types(old, new)
            for old, new in zip(original, validated, strict=True)
        )
    if isinstance(original, (set, frozenset)):
        return all(
            any(_same_types(old, new) and old == new for new in validated)
            for old in original
        )
    return True
