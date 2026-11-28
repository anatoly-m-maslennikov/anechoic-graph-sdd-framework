"""Compile declared Markdown Content properties into a Workbench SQL schema."""

from __future__ import annotations

from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass

from collections.abc import Iterable as Iterable
from collections.abc import Mapping, Sequence
from dataclasses import field
import json
from pathlib import Path
import re as re
from typing import Annotated, Any

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared import formal_claim_blocks as \
    formal_claim_blocks  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        content_record_span,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        records_by_path,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        is_current_requirement_declaration as is_current_requirement_declaration,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        matches_carrier_label,
    )  # fmt: skip

from ._content_rules import (
    content_schema_from_statements as content_schema_from_statements,
    declaration_statements as declaration_statements,
    _seed_summary,
    _declared_children as _declared_children,
    _rule_key as _rule_key,
    _schema_from_rules as _schema_from_rules,
    _source as _source,
    _source_key as _source_key,
    _statement_rules as _statement_rules,
)
from ...content_values import (
    _legacy_prose_claim as _legacy_prose_claim,
    _prose_claim as _prose_claim,
    _value,
)
from ...declaration_ancestry import compile_ancestry as compile_ancestry
from ... import declaration_cfel as _cfel
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        content_lines,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        parse_content,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        source_markdown,
    )  # fmt: skip

_container = _cfel.container
_filters = _cfel.filters
intersect_selectors = _cfel.intersect_selectors
_model_statements = _cfel.model_statements
_segments = _cfel.segments
selector_key = _cfel.selector_key


def _retain_mapping(value, handler):
    handler(value)
    return value


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class DeclarationSource:
    """One Current Declaration which contributed to the compiled schema."""

    reference: str | None
    version: int | None
    source_path: str | None

    def asset(self) -> dict[str, object]:
        return {
            "reference": self.reference,
            "version": self.version,
            "source_path": self.source_path,
        }


FormalStatement = tuple[str, DeclarationSource]


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ContentRule:
    """A literal declared Content path and its narrow applicability."""

    path: tuple[str, ...]
    roles: frozenset[str] | None
    forms: frozenset[str] | None
    value_bearing: bool
    source: DeclarationSource
    prohibited: bool = False
    provenance: tuple[DeclarationSource, ...] = ()

    def applies(self, row: Mapping[str, Any]) -> bool:
        return (
            self.roles is None
            or matches_carrier_label(row.get("role"), self.roles)
        ) and (
            self.forms is None
            or matches_carrier_label(row.get("form"), self.forms)
        )


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ContentColumn:
    """One declared scalar Markdown property exposed as a VARCHAR column."""

    path: tuple[str, ...]
    name: str
    rules: tuple[ContentRule, ...]

    def applies(self, row: Mapping[str, Any]) -> bool:
        return any(rule.applies(row) for rule in self.rules)


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ContentSchema:
    """The reproducible Content portion of the public atoms schema."""

    columns: tuple[ContentColumn, ...]
    rules: tuple[ContentRule, ...]
    sources: tuple[DeclarationSource, ...]
    _layouts: Annotated[
        dict[
            tuple[str | None, str | None],
            tuple[Any, frozenset[tuple[str, ...]]],
        ],
        WrapValidator(_retain_mapping),
    ] = field(
        default_factory=dict,
        compare=False,
        repr=False,
    )

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @property
    def shape(self) -> tuple[tuple[object, ...], tuple[object, ...]]:
        """The table/validation shape, excluding declaration provenance."""
        return (
            tuple((column.path, column.name) for column in self.columns),
            tuple(
                sorted(
                    {
                        (
                            rule.path,
                            selector_key(rule.roles),
                            selector_key(rule.forms),
                            rule.value_bearing,
                            rule.prohibited,
                        )
                        for rule in self.rules
                    }
                )
            ),
        )

    def values(self, row: Mapping[str, Any]) -> dict[str, str | None]:
        """Extract Content values and reject duplicate declared headings."""
        records = row.get("content_properties_json")
        body = source_markdown(row)
        if not isinstance(records, list):
            records = (
                parse_content(body, tolerate_duplicate_siblings=True)
                if isinstance(body, str)
                else []
            )
        elif isinstance(body, str) and any(
            not isinstance(record, Mapping)
            or content_record_span(record) is None
            for record in records
        ):
            records = parse_content(body, tolerate_duplicate_siblings=True)
        values = records_by_path(records)
        if row.get("status_group") != "Archived" and not row.get(
            "_retain_parsed"
        ):
            self._validate(values, row)
        lines = content_lines(body) if isinstance(body, str) else None
        layout, _ = self._layout(row)
        projected = {
            column.name: _value(
                values,
                column.path,
                applies,
                children,
                lines,
            )
            for column, applies, children in layout
        }
        _seed_summary(row, records, projected)
        return projected

    def validate(self, row: Mapping[str, Any]) -> None:
        """Check duplicate declared paths without extracting SQL columns."""
        records = row.get("content_properties_json")
        if not isinstance(records, list):
            body = source_markdown(row)
            records = (
                parse_content(body, tolerate_duplicate_siblings=True)
                if isinstance(body, str)
                else []
            )
        self._validate(records_by_path(records), row)

    def _validate(
        self,
        values: Mapping[tuple[str, ...], list[Mapping[str, Any]]],
        row: Mapping[str, Any],
    ) -> None:
        duplicates = {
            path for path, entries in values.items() if len(entries) > 1
        }
        if duplicates:
            _, declared = self._layout(row)
            if conflict := next(iter(sorted(duplicates & declared)), None):
                raise ValueError(
                    "duplicate declared content property: "
                    f"{'.'.join(conflict)}"
                )

    def _layout(
        self, row: Mapping[str, Any]
    ) -> tuple[Any, frozenset[tuple[str, ...]]]:
        role = row.get("role") if isinstance(row.get("role"), str) else None
        form = row.get("form") if isinstance(row.get("form"), str) else None
        key = (role, form)
        cached = self._layouts.get(key)
        if cached is not None:
            return cached
        applicable = tuple(
            rule
            for rule in self.rules
            if not rule.prohibited
            and not any(part in {"*", "**"} for part in rule.path)
            and rule.applies(row)
        )
        children: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
        for rule in applicable:
            children.setdefault(rule.path[:-1], set()).add(rule.path)
        layout = tuple(
            (
                column,
                column.applies(row),
                frozenset(children.get(column.path, ())),
            )
            for column in self.columns
        )
        result = (layout, frozenset(rule.path for rule in applicable))
        self._layouts[key] = result
        return result

    def asset(self) -> dict[str, object]:
        return {
            "version": 1,
            "content_columns": [
                {
                    "path": list(column.path),
                    "name": column.name,
                    "format": "VARCHAR",
                    "rules": [
                        {
                            "roles": sorted(rule.roles)
                            if rule.roles is not None
                            else None,
                            "forms": sorted(rule.forms)
                            if rule.forms is not None
                            else None,
                            "source": rule.source.asset(),
                            "provenance": [
                                source.asset() for source in rule.provenance
                            ],
                        }
                        for rule in column.rules
                    ],
                }
                for column in self.columns
            ],
            "content_declaration_sources": [
                source.asset() for source in self.sources
            ],
        }

    def write(self, path: Path | None) -> None:
        if path is not None:
            path.write_text(
                json.dumps(self.asset(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def content_schema_asset_path(database_path: Path | None) -> Path | None:
    """Keep the Content schema beside the projection."""
    return (
        database_path.parent / "content-schema.json"
        if database_path is not None
        else None
    )


def compile_content_schema(
    atom_rows: Sequence[Mapping[str, Any]],
) -> ContentSchema:
    """Compile only named declarations into paths."""
    return content_schema_from_statements(
        statement
        for row in atom_rows
        for statement in declaration_statements(row)
    )
