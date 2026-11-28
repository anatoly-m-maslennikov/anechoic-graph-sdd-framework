"""Build the Workbench Header SQL schema from raw source Headers."""

from __future__ import annotations

from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass

from collections.abc import Mapping, Sequence
from dataclasses import field
import datetime as dt
import json
from pathlib import Path
from typing import Annotated, Any

from .declared_header_rules import HeaderRule, compile_header_rules
from .._header_observed_values import (
    _Contribution as _Contribution,
    _add,
    _collect_contribution as _collect_contribution,
    _column_name,
    _contribution,
    _decrement as _decrement,
    _empty as _empty,
    _matches_format,
    _remove,
    _source_key,
    _value_format as _value_format,
)
from .header_column_rules import (
    _reader_name,
    _rule_applies,
    _rule_asset,
    _rule_key,
    _rule_shape,
    _selector_metadata,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        json_value as json_value,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        canonical as canonical,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        header_field_paths,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        header_value,
    )  # fmt: skip


def _retain_mapping(value, handler):
    handler(value)
    return value


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class HeaderColumn:
    """One source-faithful Header value."""

    path: tuple[str, ...]
    name: str
    format: str
    populated: bool
    reader: str | None = None
    rules: tuple[HeaderRule, ...] = ()

    def applies(self, row: Mapping[str, Any]) -> bool:
        return not self.rules or any(
            _rule_applies(rule, row) for rule in self.rules
        )


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class HeaderSchema:
    """The derived, reproducible Header part of the public atoms schema."""

    columns: tuple[HeaderColumn, ...]

    @property
    def shape(self) -> tuple[tuple[object, ...], ...]:
        """Table shape without declaration provenance."""
        return tuple(
            (
                column.path,
                column.name,
                column.format,
                column.populated,
                column.reader,
                tuple(sorted({_rule_shape(rule) for rule in column.rules})),
            )
            for column in self.columns
        )

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @property
    def json_names(self) -> frozenset[str]:
        return frozenset(
            column.name for column in self.columns if column.format == "JSON"
        )

    @property
    def status_names(self) -> tuple[str, ...]:
        return tuple(
            column.name
            for column in self.columns
            if column.path[-1:] == ("status",) and column.format == "VARCHAR"
        )

    def value(self, row: Mapping[str, Any], column: HeaderColumn) -> Any:
        if not column.applies(row):
            return None
        header = row.get("header_json")
        if column.reader is not None:
            if not isinstance(header, dict):
                return None
            present, resolved = header_value(header, column.reader)
            if not present:
                return None
            if column.format == "TIMESTAMPTZ":
                timestamp = (
                    dt.datetime.fromisoformat(resolved.replace("Z", "+00:00"))
                    if isinstance(resolved, str)
                    else resolved
                )
                if isinstance(timestamp, dt.datetime) and (
                    timestamp.tzinfo is None or timestamp.utcoffset() is None
                ):
                    raise ValueError(
                        f"Header {column.reader} requires an "
                        "offset-bearing timestamp"
                    )
                return timestamp
            return resolved
        value: Any = header
        for key in column.path:
            if not isinstance(value, Mapping) or key not in value:
                return None
            value = value[key]
        return value

    def validate(self, row: Mapping[str, Any]) -> None:
        """Reject a value incompatible with its literal SQL type."""
        for column in self.columns:
            value = self.value(row, column)
            if value is not None and not _matches_format(value, column.format):
                raise ValueError(
                    f"Header {column.name} requires {column.format}"
                )

    def asset(self) -> dict[str, object]:
        return {
            "version": 1,
            "header_columns": [
                {
                    "path": list(column.path),
                    "name": column.name,
                    "format": column.format,
                    "populated": column.populated,
                    "reader": column.reader,
                    **(
                        {"rules": [_rule_asset(rule) for rule in column.rules]}
                        if column.rules
                        else {}
                    ),
                }
                for column in self.columns
            ],
        }

    def write(self, path: Path | None) -> None:
        if path is not None:
            path.write_text(
                json.dumps(self.asset(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class HeaderSchemaState:
    """Owner-local Header aggregates from exact materialized deltas."""

    direct_counts: Annotated[
        Mapping[tuple[str, ...], int], WrapValidator(_retain_mapping)
    ] = field(default_factory=dict)
    format_counts: Annotated[
        Mapping[tuple[str, ...], Mapping[str, int]],
        WrapValidator(_retain_mapping),
    ] = field(default_factory=dict)
    populated_counts: Annotated[
        Mapping[tuple[str, ...], int], WrapValidator(_retain_mapping)
    ] = field(default_factory=dict)

    @classmethod
    def from_atoms(
        cls, atom_rows: Sequence[Mapping[str, Any]]
    ) -> HeaderSchemaState:
        new_rows = {}
        for index, row in enumerate(atom_rows):
            key = _source_key(row, index)
            new_rows[key if key not in new_rows else f"<row:{index}>"] = row
        return cls().updated({}, new_rows)

    @property
    def schema(self) -> HeaderSchema:
        names: dict[str, tuple[str, ...]] = {}
        columns = []
        for path in sorted(self.direct_counts, key=_column_name):
            name = _column_name(path)
            previous = names.setdefault(name, path)
            if previous != path:
                raise ValueError(
                    f"Header SQL column collision: {'.'.join(previous)} "
                    f"and {'.'.join(path)} -> {name}"
                )
            formats = self.format_counts.get(path, {})
            columns.append(
                HeaderColumn(
                    path,
                    name,
                    next(iter(formats)) if len(formats) == 1 else "JSON",
                    self.populated_counts.get(path, 0) > 0,
                )
            )
        return HeaderSchema(tuple(columns))

    def updated(
        self,
        old_rows: Mapping[str, Mapping[str, Any]],
        new_rows: Mapping[str, Mapping[str, Any]],
    ) -> HeaderSchemaState:
        """Subtract old source rows and add new ones to a candidate state."""
        direct_counts = dict(self.direct_counts)
        format_counts = {
            path: dict(counts) for path, counts in self.format_counts.items()
        }
        populated_counts = dict(self.populated_counts)
        for rows, update in ((old_rows, _remove), (new_rows, _add)):
            for source_path, row in rows.items():
                if not isinstance(source_path, str) or not source_path:
                    raise ValueError(
                        "Header source path must be a non-empty string"
                    )
                if (contribution := _contribution(row)) is not None:
                    update(
                        contribution,
                        direct_counts,
                        format_counts,
                        populated_counts,
                    )
        return HeaderSchemaState(
            direct_counts, format_counts, populated_counts
        )


def schema_asset_path(database_path: Path | None) -> Path | None:
    return (
        database_path.parent / "projection-schema.json"
        if database_path is not None
        else None
    )


def infer_header_schema(
    atom_rows: Sequence[Mapping[str, Any]],
) -> HeaderSchema:
    """Return observed Header columns; relations stay graph materialized."""
    return HeaderSchemaState.from_atoms(atom_rows).schema


def declared_header_schema(rules: Sequence[HeaderRule]) -> HeaderSchema:
    """Bind literal model Header declarations to the carrier adapter."""
    grouped: dict[tuple[tuple[str, ...], str, str, str], list[HeaderRule]] = {}
    names: dict[str, tuple[tuple[str, ...], str, str]] = {}
    for rule in sorted(rules, key=_rule_key):
        if rule.format is None:
            continue
        reader = _reader_name(rule)
        if reader == "relations":
            continue
        path = header_field_paths(reader, _selector_metadata(rule))[0]
        name = _column_name(path)
        previous = names.setdefault(name, (path, rule.format, reader))
        if previous[:2] != (path, rule.format):
            raise ValueError(
                f"Header SQL declaration collision: {name} "
                "has incompatible model declarations"
            )
        grouped.setdefault((path, name, rule.format, previous[2]), []).append(
            rule
        )
    return HeaderSchema(
        tuple(
            HeaderColumn(
                path,
                name,
                format_name,
                False,
                reader,
                tuple(sorted(set(column_rules), key=_rule_key)),
            )
            for (path, name, format_name, reader), column_rules in sorted(
                grouped.items(), key=lambda item: item[0][1]
            )
        )
    )


def header_schema_for_mode(
    mode: int,
    atom_rows: Sequence[Mapping[str, Any]],
    *,
    header_rules: Sequence[HeaderRule] | None = None,
) -> HeaderSchema:
    """Compile exactly the selected cold-start Header projection."""
    if mode == 1:
        return declared_header_schema(
            compile_header_rules(atom_rows)
            if header_rules is None
            else header_rules
        )
    if mode == 2:
        return infer_header_schema(atom_rows)
    raise ValueError("workbench.schema_mode must be 1 or 2")
