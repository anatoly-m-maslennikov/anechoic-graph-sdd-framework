"""Compile Content declarations into schema rules."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from . import content_schema as runtime


def _schema_from_rules(
    rules: Iterable[runtime.ContentRule],
) -> runtime.ContentSchema:
    """Assemble a schema from already parsed declaration rules."""
    unique_rules = tuple(sorted(set(rules), key=runtime._rule_key))
    sources = tuple(
        sorted(
            {
                source
                for rule in unique_rules
                for source in (rule.source, *rule.provenance)
            },
            key=runtime._source_key,
        )
    )
    grouped: dict[tuple[str, ...], list[runtime.ContentRule]] = {}
    for rule in unique_rules:
        if rule.value_bearing and not any(
            part in {"*", "**"} for part in rule.path
        ):
            grouped.setdefault(rule.path, []).append(rule)
    columns = tuple(
        runtime.ContentColumn(
            path, "content." + ".".join(path), tuple(grouped[path])
        )
        for path in sorted(
            grouped, key=lambda path: "content." + ".".join(path)
        )
    )
    return runtime.ContentSchema(columns, unique_rules, sources)


def _source(row: Mapping[str, Any]) -> runtime.DeclarationSource:
    reference = row.get("ref")
    atom_id = row.get("id")
    source_path = row.get("source_path")
    version = row.get("version")
    return runtime.DeclarationSource(
        reference
        if isinstance(reference, str)
        else atom_id
        if isinstance(atom_id, str)
        else None,
        version if type(version) is int else None,
        source_path if isinstance(source_path, str) else None,
    )


def _declared_children(
    rules: Sequence[runtime.ContentRule],
    parent_path: tuple[str, ...],
    row: Mapping[str, Any],
) -> frozenset[tuple[str, ...]]:
    return frozenset(
        rule.path
        for rule in rules
        if rule.applies(row) and rule.path[:-1] == parent_path
    )


def _statement_rules(
    statement: str,
    source: runtime.DeclarationSource,
    inherited_roles: frozenset[str] | None,
    inherited_forms: frozenset[str] | None,
    provenance: tuple[runtime.DeclarationSource, ...],
) -> list[runtime.ContentRule]:
    if (
        not statement.startswith("Atom")
        or ";>" in statement
        or "((" in statement
    ):
        return []
    content = statement.find(".Content")
    if content < 0:
        return []
    prefix, tail = statement[:content], statement[content + len(".Content") :]
    segments, remainder = runtime._segments(tail)
    if not segments:
        return []
    roles = runtime.intersect_selectors(
        runtime._filters(prefix, "Role"), inherited_roles
    )
    forms = runtime.intersect_selectors(
        runtime._filters(prefix, "Form"), inherited_forms
    )
    if segments[-1] in {"*", "**"}:
        if runtime.re.match(r"\s*\[\s*\]\s*\{\s*::\s*0\s*\}", remainder):
            return _prohibited_rule(segments, roles, forms, source, provenance)
    return [
        runtime.ContentRule(
            tuple(segments),
            roles,
            forms,
            not runtime._container(remainder),
            source,
            provenance=provenance,
        )
    ]


def _prohibited_rule(segments, roles, forms, source, provenance):
    return [
        runtime.ContentRule(
            tuple(segments),
            roles,
            forms,
            False,
            source,
            prohibited=True,
            provenance=provenance,
        )
    ]


def _source_key(source: runtime.DeclarationSource) -> tuple[str, int, str]:
    return (
        source.reference or "",
        source.version or -1,
        source.source_path or "",
    )


def _rule_key(rule: runtime.ContentRule) -> tuple[object, ...]:
    return (
        rule.path,
        runtime.selector_key(rule.roles),
        runtime.selector_key(rule.forms),
        rule.value_bearing,
        rule.prohibited,
        runtime._source_key(rule.source),
        tuple(runtime._source_key(source) for source in rule.provenance),
    )


def content_schema_from_statements(
    statements: Iterable[runtime.FormalStatement],
) -> runtime.ContentSchema:
    return runtime._schema_from_rules(
        rule
        for projected in runtime.compile_ancestry(statements)
        for rule in runtime._statement_rules(
            projected.statement,
            projected.source,
            projected.roles,
            projected.forms,
            tuple(dict.fromkeys(projected.provenance[:-1])),
        )
    )


def declaration_statements(
    row: Mapping[str, Any] | None,
) -> tuple[runtime.FormalStatement, ...]:
    """Capture formal statements, including declarations with no properties."""
    if row is None or not runtime.is_current_requirement_declaration(row):
        return ()
    body = runtime.source_markdown(row)
    if not isinstance(body, str):
        return ()
    source = runtime._source(row)
    return tuple(
        (statement, source)
        for block in runtime.formal_claim_blocks(
            body, model_class_bindings=row.get("_model_class_bindings")
        )
        for statement in runtime._model_statements(block)
    )


def _seed_summary(row, records, projected):
    header = row.get("header_json")
    context = (
        header.get("context") if isinstance(header, runtime.Mapping) else None
    )
    if (
        "content.summary" in projected
        and isinstance(context, runtime.Mapping)
        and context.get("template") == "component_seed_manifest"
    ):
        projected["content.summary"] = next(
            (
                record["heading"]
                for record in records
                if record.get("heading_level") == 1
            ),
            projected["content.summary"],
        )
