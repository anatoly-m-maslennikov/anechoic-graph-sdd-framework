"""Compile a bounded subset of explicit Header property declarations.

Compile explicit property, value and child cardinality and literal domains.
"""

import re

from . import header_constraint_compile as _compiler

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    iter_formal_claims,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim as parse_native_model_claim,
)
from ....ADAPTERS_C30.model.cardinality__pub import (
    cardinality_bounds as cardinality_bounds,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    GROUP_FIELDS,
    ROLE_FIELDS,
    header_value,
    path_value,
)

_PATH = r"[A-Za-z][A-Za-z0-9_ ]*(?:\.[A-Za-z][A-Za-z0-9_ ]*)*"
_SELECTED = r'(?:"[^"\r\n]+"|[A-Za-z][A-Za-z0-9 &_-]*)'
_SELECTOR = (
    rf"(?:/\(\s*\.Header\.(?:Context\.)?(Role|Form)\s*"
    rf"((?::=|:)\s*{_SELECTED}|in\s*\(\s*{_SELECTED}\s*\))\s*\))?"
)


def _path(value):
    parts = [re.sub(r"\s+", "_", p.strip()).lower() for p in value.split(".")]
    if len(parts) > 1 and parts[0] in GROUP_FIELDS:
        group, leaf = parts[:2]
        if group == "identity" and leaf == "id":
            parts[:2] = ["atom_id"]
        elif leaf in GROUP_FIELDS[group]:
            parts.pop(0)
        elif (
            group == "context"
            and len(parts) > 2
            and parts[2] in ROLE_FIELDS.get(leaf, ())
        ):
            parts = parts[2:]
    parts[0] = {"id": "atom_id", "carrier_destination": "destination"}.get(
        parts[0], parts[0]
    )
    return ".".join(parts)


def _value(view, path):
    return header_value(view, _path(path))


def _group(metadata, name, fields):
    _, stored = path_value(metadata, tuple(name.split(".")))
    values = (
        {_path(key): value for key, value in stored.items()}
        if isinstance(stored, dict)
        else {}
    )
    for field in fields:
        address = f"{name}.{field}" if "." in name else field
        present, value = header_value(metadata, address)
        if present:
            values[field] = value
    return values


def _logical_groups(metadata, role):
    projection = dict(metadata)
    for group, fields in GROUP_FIELDS.items():
        values = _group(metadata, group, fields)
        if values:
            projection[group] = values
    for group, fields in ROLE_FIELDS.items():
        if matches_named_value(role, group.capitalize()):
            values = _group(metadata, f"context.{group}", fields)
            if values:
                projection.setdefault("context", {})[group] = values
    return projection


def _selected(value):
    if value is None:
        return ""
    text = (
        value.partition("(")[2][:-1]
        if value.startswith("in")
        else value.lstrip(":=")
    )
    return text.strip().strip('"')


def _native_header_target(args, source):
    if args.get("relation_name") != "IS_PROPERTY_OF":
        return None
    base, name = args.get("base_path"), args.get("entity_name")
    if not isinstance(base, str) or not isinstance(name, str):
        return None
    match = re.fullmatch(rf"Atom{_SELECTOR}\.Header(?:\.({_PATH}))?", base)
    if match is None:
        return None
    selector, selected, rest = match.groups()
    selector, selected = (
        (selector.lower(), _selected(selected)) if selector else ("", "")
    )
    roles = args.get("applies_to_entity_classes", ())
    if roles:
        if (
            len(roles) != 1
            or selector
            and (selector != "role" or selected != roles[0])
        ):
            raise ValueError(f"{source}: unsupported Header Entity selector")
        selector, selected = "role", roles[0]
    return (
        _path(".".join(part for part in (rest, name) if part)),
        selector,
        selected,
    )


def _native_header_records(code, source):
    return _compiler.native_header_records(code, source)


def compile_header_constraints(rows):
    records = set()
    for row in rows:
        for block in iter_formal_claims(row["_content_bytes"].decode("utf-8")):
            records.update(_native_header_records(block, row["id"]))
    keys = ("kind", "path", "selector", "selected", "value", "source")
    return [
        dict(zip(keys, item, strict=False))
        for item in sorted(records, key=repr)
    ]


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class HeaderConstraints:
    properties: tuple[tuple[str, str, str, str, str], ...]
    domains: tuple[tuple[str, str, str, frozenset[str], str], ...]
    children: tuple[tuple[str, str, str, tuple[int | str, ...], str], ...] = ()
    values: tuple[tuple[str, str, str, tuple[int, int | None], str], ...] = ()

    def validate(self, view, *, metadata=None):
        metadata = _logical_groups(
            view if metadata is None else metadata, view.get("role")
        )
        errors = []
        self._validate_properties(view, metadata, errors)
        for path, selector, selected, values, source in self.domains:
            if selector and not matches_named_value(
                view.get(selector), selected
            ):
                continue
            present, current = _value(metadata, path)
            named = _path(path) in {"role", "form", "status"}
            actual = current if isinstance(current, list) else [current]
            if present and any(
                not isinstance(item, str)
                or not any(
                    matches_named_value(item, value)
                    if named
                    else item == value
                    for value in values
                )
                for item in actual
            ):
                errors.append(
                    (
                        path,
                        f"Header {path} must use a declared value ({source}).",
                        values,
                    )
                )
        errors.extend(self._validate_children(view, metadata))
        errors.extend(self._validate_values(view, metadata))
        return errors

    def _validate_properties(self, view, metadata, errors):
        for path, selector, selected, count, source in self.properties:
            if selector and not matches_named_value(
                view.get(selector), selected
            ):
                continue
            logical = _path(path)
            parent_path = logical.rpartition(".")[0]
            if parent_path and not isinstance(
                _value(metadata, parent_path)[1], dict
            ):
                continue
            present, _ = _value(metadata, logical)
            if (count == "1" and not present) or (count == "0" and present):
                field = (
                    self._missing_field(view, logical) if not present else path
                )
                errors.append(
                    (
                        field,
                        f"Header {path} requires property cardinality "
                        f"{count} ({source}).",
                        None,
                    )
                )

    def _validate_values(self, view, metadata):
        for path, selector, selected, (low, high), source in self.values:
            if selector and not matches_named_value(
                view.get(selector), selected
            ):
                continue
            wildcard = path.endswith(".*")
            present, value = _value(metadata, path[:-2] if wildcard else path)
            if not present:
                continue
            entries = (
                value.items()
                if wildcard and isinstance(value, dict)
                else ()
                if wildcard
                else ((None, value),)
            )
            for child, item in entries:
                count = (
                    0
                    if isinstance(item, dict)
                    else len(item)
                    if isinstance(item, list)
                    else 1
                )
                if count < low or (high is not None and count > high):
                    field = f"{path[:-2]}.{child}" if wildcard else path
                    expected = (
                        f"{low}+"
                        if high is None
                        else str(low)
                        if low == high
                        else f"{low}..{high}"
                    )
                    yield (
                        field,
                        f"Header {field} requires value cardinality "
                        f"{expected} ({source}).",
                        None,
                    )

    def _missing_field(self, view, path):
        for group, selector, selected, bounds, _ in self.children:
            if (
                _path(group) == path
                and bounds[:2] == (1, 1)
                and len(bounds) == 3
                and (
                    not selector
                    or matches_named_value(view.get(selector), selected)
                )
            ):
                return _path(f"{path}.{bounds[2]}")
        return path

    def _validate_children(self, view, metadata):
        for path, selector, selected, value, source in self.children:
            if selector and not matches_named_value(
                view.get(selector), selected
            ):
                continue
            present, group = _value(metadata, path)
            if not present:
                continue
            low, high, *names = value
            keys = set(group) if isinstance(group, dict) else set()
            if not low <= len(keys) <= high or keys - set(names):
                yield (
                    path,
                    f"Header {path} requires {low}..{high} children from "
                    f"{', '.join(names)} ({source}).",
                    None,
                )


def load_header_constraints(records, source_ids):
    return _compiler.load_header_constraints(records, source_ids)
