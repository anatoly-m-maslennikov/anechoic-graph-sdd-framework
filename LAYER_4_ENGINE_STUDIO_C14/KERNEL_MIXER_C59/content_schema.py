
"""Compile declared Markdown Content properties into a Workbench SQL schema."""

from __future__ import annotations

from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import field
import json
from pathlib import Path
import re
from typing import Annotated, Any

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import formal_claim_blocks
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import content_record_span
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import records_by_path
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import is_current_requirement_declaration, matches_carrier_label

from .content_values import _legacy_prose_claim as _legacy_prose_claim, _prose_claim as _prose_claim, _value
from .declaration_ancestry import compile_ancestry
from .declaration_cfel import (
    container as _container, filters as _filters,
    intersect_selectors,
    model_statements as _model_statements, segments as _segments, selector_key,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import content_lines, parse_content, source_markdown


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
            tuple(sorted({
                (rule.path, selector_key(rule.roles), selector_key(rule.forms),
                 rule.value_bearing, rule.prohibited)
                for rule in self.rules
            })),
        )

    def values(self, row: Mapping[str, Any]) -> dict[str, str | None]:
        """Extract declared Content values and reject duplicate declared headings."""
        records = row.get("content_properties_json")
        body = source_markdown(row)
        if not isinstance(records, list):
            records = parse_content(body, tolerate_duplicate_siblings=True) if isinstance(body, str) else []
        elif isinstance(body, str) and any(
            not isinstance(record, Mapping)
            or content_record_span(record) is None
            for record in records
        ):
            records = parse_content(body, tolerate_duplicate_siblings=True)
        values = records_by_path(records)
        if row.get("status_group") != "Archived" and not row.get("_retain_parsed"):
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
        header = row.get("header_json")
        context = header.get("context") if isinstance(header, Mapping) else None
        if ("content.summary" in projected and isinstance(context, Mapping)
                and context.get("template") == "component_seed_manifest"):
            projected["content.summary"] = next(
                (record["heading"] for record in records if record.get("heading_level") == 1),
                projected["content.summary"],
            )
        return projected

    def validate(self, row: Mapping[str, Any]) -> None:
        """Check duplicate declared paths without extracting every SQL column."""
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
        self, values: Mapping[tuple[str, ...], list[Mapping[str, Any]]], row: Mapping[str, Any],
    ) -> None:
        duplicates = {path for path, entries in values.items() if len(entries) > 1}
        if duplicates:
            _, declared = self._layout(row)
            if conflict := next(iter(sorted(duplicates & declared)), None):
                raise ValueError(f"duplicate declared content property: {'.'.join(conflict)}")

    def _layout(self, row: Mapping[str, Any]) -> tuple[Any, frozenset[tuple[str, ...]]]:
        role = row.get("role") if isinstance(row.get("role"), str) else None
        form = row.get("form") if isinstance(row.get("form"), str) else None
        key = (role, form)
        cached = self._layouts.get(key)
        if cached is not None:
            return cached
        applicable = tuple(
            rule for rule in self.rules if not rule.prohibited
            and not any(part in {"*", "**"} for part in rule.path) and rule.applies(row)
        )
        children: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
        for rule in applicable:
            children.setdefault(rule.path[:-1], set()).add(rule.path)
        layout = tuple(
            (column, column.applies(row), frozenset(children.get(column.path, ())))
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
                            "provenance": [source.asset() for source in rule.provenance],
                        }
                        for rule in column.rules
                    ],
                }
                for column in self.columns
            ],
            "content_declaration_sources": [source.asset() for source in self.sources],
        }

    def write(self, path: Path | None) -> None:
        if path is not None:
            path.write_text(
                json.dumps(self.asset(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def content_schema_asset_path(database_path: Path | None) -> Path | None:
    """Keep the independently rebuildable Content schema beside the projection."""
    return database_path.parent / "content-schema.json" if database_path is not None else None


def compile_content_schema(atom_rows: Sequence[Mapping[str, Any]]) -> ContentSchema:
    """Compile only named declarations; headings and constraints do not create paths."""
    return content_schema_from_statements(
        statement for row in atom_rows for statement in declaration_statements(row)
    )


def content_schema_from_statements(statements: Iterable[FormalStatement]) -> ContentSchema:
    return _schema_from_rules(
        rule for projected in compile_ancestry(statements)
        for rule in _statement_rules(
            projected.statement, projected.source, projected.roles, projected.forms,
            tuple(dict.fromkeys(projected.provenance[:-1])),
        )
    )


def declaration_statements(row: Mapping[str, Any] | None) -> tuple[FormalStatement, ...]:
    """Capture formal statements, including declarations with no properties."""
    if row is None or not is_current_requirement_declaration(row):
        return ()
    body = source_markdown(row)
    if not isinstance(body, str):
        return ()
    source = _source(row)
    return tuple(
        (statement, source)
        for block in formal_claim_blocks(body, model_class_bindings=row.get("_model_class_bindings"))
        for statement in _model_statements(block)
    )


def _schema_from_rules(rules: Iterable[ContentRule]) -> ContentSchema:
    """Assemble a schema from already parsed declaration rules."""
    unique_rules = tuple(sorted(set(rules), key=_rule_key))
    sources = tuple(sorted(
        {source for rule in unique_rules for source in (rule.source, *rule.provenance)},
        key=_source_key,
    ))
    grouped: dict[tuple[str, ...], list[ContentRule]] = {}
    for rule in unique_rules:
        if rule.value_bearing and not any(part in {"*", "**"} for part in rule.path):
            grouped.setdefault(rule.path, []).append(rule)
    columns = tuple(
        ContentColumn(path, "content." + ".".join(path), tuple(grouped[path]))
        for path in sorted(grouped, key=lambda path: "content." + ".".join(path))
    )
    return ContentSchema(columns, unique_rules, sources)


def _source(row: Mapping[str, Any]) -> DeclarationSource:
    reference = row.get("ref")
    atom_id = row.get("id")
    source_path = row.get("source_path")
    version = row.get("version")
    return DeclarationSource(
        reference if isinstance(reference, str) else atom_id if isinstance(atom_id, str) else None,
        version if type(version) is int else None,
        source_path if isinstance(source_path, str) else None,
    )


def _declared_children(
    rules: Sequence[ContentRule], parent_path: tuple[str, ...], row: Mapping[str, Any],
) -> frozenset[tuple[str, ...]]:
    return frozenset(
        rule.path
        for rule in rules
        if rule.applies(row) and rule.path[:-1] == parent_path
    )


def _statement_rules(
    statement: str, source: DeclarationSource,
    inherited_roles: frozenset[str] | None, inherited_forms: frozenset[str] | None,
    provenance: tuple[DeclarationSource, ...],
) -> list[ContentRule]:
    if not statement.startswith("Atom") or ";>" in statement or "((" in statement:
        return []
    content = statement.find(".Content")
    if content < 0:
        return []
    prefix, tail = statement[:content], statement[content + len(".Content") :]
    segments, remainder = _segments(tail)
    if not segments:
        return []
    roles = intersect_selectors(_filters(prefix, "Role"), inherited_roles)
    forms = intersect_selectors(_filters(prefix, "Form"), inherited_forms)
    if segments[-1] in {"*", "**"}:
        if re.match(r"\s*\[\s*\]\s*\{\s*::\s*0\s*\}", remainder):
            return [ContentRule(tuple(segments), roles, forms, False, source, prohibited=True, provenance=provenance)]
        return [ContentRule(tuple(segments), roles, forms, not _container(remainder), source, provenance=provenance)]
    return [ContentRule(tuple(segments), roles, forms, not _container(remainder), source, provenance=provenance)]


def _source_key(source: DeclarationSource) -> tuple[str, int, str]:
    return (source.reference or "", source.version or -1, source.source_path or "")


def _rule_key(rule: ContentRule) -> tuple[object, ...]:
    return (
        rule.path,
        selector_key(rule.roles),
        selector_key(rule.forms),
        rule.value_bearing,
        rule.prohibited,
        _source_key(rule.source),
        tuple(_source_key(source) for source in rule.provenance),
    )
