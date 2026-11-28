"""Collect per-source Atom diagnostics."""

import re


def _collect_sources(
    sources, context, audits, schema_invalid, checkers, table_names
):
    root, paths, cached, diagnostics, accepted = sources
    scope_paths, project_scope_id, schema, public_atoms = context
    issues_for_source, content_issues = checkers
    tables, schema_issues = table_names
    result: dict[str, list[tuple[str | None, ...]]] = {
        table: [] for table in tables
    }
    layouts: dict[
        tuple[str | None, str | None], dict[tuple[str, ...], str]
    ] = {}
    prefix = re.escape(project_scope_id.removesuffix("-SU-00"))
    atom_name = re.compile(rf"(?:[1-9][0-9]*-)?{prefix}-[A-Z]-[0-9]+")
    for path in sorted(paths):
        row = cached.get(path, (None, None))[1]
        relative = path.relative_to(root)
        public = public_atoms.get((relative.parent.as_posix(), path.name))
        diagnostic = diagnostics.get(path)
        if (
            row is None
            and path not in schema_invalid
            and not atom_name.match(path.name)
        ):
            continue
        issues = _source_issues(
            relative,
            row,
            diagnostic,
            scope_paths,
            audits,
            path in schema_invalid,
            issues_for_source,
        )
        _add_content_issues(
            (row, path in accepted, diagnostic, relative, public),
            (issues, schema_issues, content_issues, schema, layouts),
        )
        for table, records in issues.items():
            result[table].extend(records)
    return result


def _add_content_issues(source, audit):
    row, accepted, diagnostic, relative, public = source
    issues, schema_issues, content_issues, schema, layouts = audit
    if (
        row is not None
        and row.get("status_group") != "Archived"
        and accepted
        and not issues[schema_issues]
        and not diagnostic
    ):
        issues[schema_issues].extend(
            content_issues(relative, row, schema, public, layouts)
        )


def _source_issues(
    relative,
    row,
    diagnostic,
    scope_paths,
    audits,
    schema_error,
    issues_for_source,
):
    role_folders, schema_audit, placement_audit = audits
    return issues_for_source(
        relative.as_posix(),
        row,
        diagnostic,
        scope_paths=scope_paths,
        role_folders=role_folders,
        schema_error=schema_error,
        schema_audit=schema_audit,
        placement_audit=placement_audit,
    )
