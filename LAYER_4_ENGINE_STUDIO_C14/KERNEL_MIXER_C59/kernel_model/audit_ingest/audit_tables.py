"""Query-visible diagnostics derived from the selected Atom source scan."""

from __future__ import annotations

from pathlib import Path
from typing import AbstractSet, Any, Iterable, Mapping

from .audit_storage import (
    PARSE_ISSUES as PARSE_ISSUES,
    SCHEMA_ISSUES as SCHEMA_ISSUES,
    DECLARED_CARRIER_ISSUES as DECLARED_CARRIER_ISSUES,
    PHYSICAL_CARRIER_ISSUES as PHYSICAL_CARRIER_ISSUES,
    TABLES as TABLES,
    COLUMNS as COLUMNS,
)
from .audit_content_query import query_content_rows as query_content_rows
from . import audit_revisions, audit_storage
from .audit_content_issues import _content_issues
from ...audit_collection import _collect_sources
from .audit_placement import _check_placement

from ...errors import WorkbenchUnavailableError
from ...content_schema import ContentSchema
from .source_inventory import (
    filename_candidate,
    filename_role_matches,
    filename_marker,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        header_value,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        atom_identifier,
    )  # fmt: skip


def create_tables(connection: Any) -> None:
    audit_storage.create_tables(connection, TABLES, COLUMNS)


def _clear(connection: Any, paths: tuple[str, ...] | None) -> None:
    audit_storage.clear(connection, paths, TABLES)


def _insert(
    connection: Any, issues: Mapping[str, list[tuple[str | None, ...]]]
):
    audit_storage.insert(connection, issues, TABLES, COLUMNS)


def publish(
    connection: Any,
    issues: Mapping[str, list[tuple[str | None, ...]]]
    | Iterable[Mapping[str, list[tuple[str | None, ...]]]],
    paths: Iterable[str] | None,
    *,
    available: bool,
) -> None:
    if not available:
        raise WorkbenchUnavailableError(
            "query store unavailable; Workbench restart required"
        )
    try:
        connection.execute("BEGIN TRANSACTION")
        selected = None if paths is None else tuple(paths)
        affected = (
            _affected_revisions(connection, selected)
            if selected is not None
            else None
        )
        _clear(connection, selected)
        for batch in (issues,) if isinstance(issues, Mapping) else issues:
            _insert(connection, batch)
        _refresh_revision_issues(connection, affected)
        connection.execute("COMMIT")
    except Exception as error:
        connection.execute("ROLLBACK")
        raise WorkbenchUnavailableError("Atom audit refresh failed") from error


def revision_query(connection: Any, *, stable_only: bool = True) -> str:
    columns = {
        row[0]
        for row in connection.execute(
            "SELECT column_name FROM information_schema.columns WHERE "
            "table_catalog=current_database() "
            "AND table_schema='main' AND table_name='atoms'"
        ).fetchall()
    }
    ids = [
        f'try_cast("{name}" AS VARCHAR)'
        for name in (
            "header.identity.atom_id",
            "header.identity.id",
            "header.atom_id",
        )
        if name in columns
    ]
    versions = [
        f'try_cast("{name}" AS BIGINT)'
        for name in (
            "header.state.version",
            "header.state.version_number",
            "header.version",
            "header.version_number",
        )
        if name in columns
    ]
    identity = "coalesce(" + ", ".join([*ids, "reference"]) + ")"
    suffix = (
        "try_cast(nullif(regexp_extract(reference, "
        "'@([1-9][0-9]*)(-draft)?$', 1), '') AS BIGINT)"
    )
    version = "coalesce(" + ", ".join([*versions, suffix]) + ")"
    return (
        "SELECT reference, relative_path, filename, "
        f"regexp_replace({identity}, '@[1-9][0-9]*(-draft)?$', '') AS atom_"
        "id, "
        f"{version} AS version FROM main.atoms"
        + (
            " WHERE status_group IN ('Current', 'Archived')"
            if stable_only
            else ""
        )
    )


def _affected_revisions(connection, paths):
    return audit_revisions.affected(connection, paths, revision_query)


def _refresh_revision_issues(connection, affected):
    return audit_revisions.refresh(connection, affected, revision_query)


def collect_issues(
    root: Path,
    control_root: Path,
    source_paths: AbstractSet[Path],
    selected: set[str] | None,
    cached: Mapping[Path, tuple[Any, dict[str, Any]]],
    diagnostics: Mapping[Path, str],
    accepted: AbstractSet[Path],
    scopes: Iterable[dict[str, Any]],
    project_scope_id: str,
    schema: ContentSchema | None,
    public_atoms: Mapping[tuple[str, str], Mapping[str, Any]],
    role_folders=None,
    schema_audit=None,
    placement_audit=None,
    schema_invalid=frozenset(),
) -> dict[str, list[tuple[str | None, ...]]]:
    scope_paths = _scope_paths(scopes)
    scope_paths[project_scope_id] = control_root.relative_to(root).as_posix()
    paths = (
        source_paths
        if selected is None
        else {root / path for path in selected}
    )
    return _collect_sources(
        (root, paths & source_paths, cached, diagnostics, accepted),
        (scope_paths, project_scope_id, schema, public_atoms),
        (role_folders, schema_audit, placement_audit),
        schema_invalid,
        (issues_for_source, _content_issues),
        (TABLES, SCHEMA_ISSUES),
    )


def _scope_paths(scopes):
    return {
        key: item["authority_path"]
        for item in scopes
        for key in (item["scope_unit_name"], item["scope_unit_id"])
        if isinstance(key, str)
    }


def issues_for_source(
    path: str,
    row: Mapping[str, Any] | None,
    diagnostic: str | None,
    *,
    scope_paths: Mapping[str, str],
    role_folders=None,
    schema_error=False,
    schema_audit=None,
    placement_audit=None,
) -> dict[str, list[tuple[str | None, ...]]]:
    result: dict[str, list[tuple[str | None, ...]]] = {
        table: [] for table in TABLES
    }
    file = Path(path)
    reference = row.get("ref") if row else None
    reference = reference if isinstance(reference, str) else None
    add = _issue_recorder(result, reference, file.parent.as_posix(), file.name)

    if diagnostic:
        if schema_error:
            add(SCHEMA_ISSUES, "schema_invalid", None, None, None, diagnostic)
        else:
            add(PARSE_ISSUES, "parse_failed", None, None, None, diagnostic)
        return result
    if row is None:
        return result
    if error := row.get("_source_schema_error"):
        add(SCHEMA_ISSUES, "schema_invalid", None, None, None, str(error))
        return result
    if schema_audit is not None:
        for issue in schema_audit(row):
            add(
                SCHEMA_ISSUES,
                "schema_invalid",
                issue["field"],
                issue.get("observed"),
                issue.get("expected"),
                issue["message"],
            )
        if result[SCHEMA_ISSUES]:
            return result
    _placement_issues(
        row, file, scope_paths, role_folders, placement_audit, add, result
    )
    return result


def _issue_recorder(result, reference, relative, filename):
    def add(
        table: str,
        category: str,
        property: str | None,
        observed: object,
        expected: object,
        message: str,
    ) -> None:
        result[table].append(
            (
                reference,
                relative,
                filename,
                category,
                property,
                _text(observed),
                _text(expected),
                message,
            )
        )

    return add


def _placement_issues(
    row, file, scope_paths, role_folders, placement_audit, add, result
):
    return _check_placement(
        row,
        file,
        scope_paths,
        role_folders,
        placement_audit,
        add,
        result,
        header_value,
        _declared_filename_issue,
        DECLARED_CARRIER_ISSUES,
        PHYSICAL_CARRIER_ISSUES,
    )


def _declared_filename_issue(
    name: object,
    declared_path: object,
    row: Mapping[str, Any],
    role_folders=None,
) -> tuple[str, object, object, str] | None:
    declared = (
        Path(declared_path) / name
        if isinstance(declared_path, str) and isinstance(name, str)
        else None
    )
    if (
        declared is not None
        and filename_candidate(declared)
        and not filename_role_matches(declared, role_folders)
    ):
        return (
            "file.name",
            name,
            declared_path,
            "The declared filename role conflicts with its declared role "
            "directory.",
        )
    if not isinstance(name, str):
        return None
    if issue := _filename_identity_issue(name, row):
        return issue
    role = row.get("role")
    marker = filename_marker(Path(name))
    if marker and isinstance(role, str) and role and marker != role[0].upper():
        return (
            "file.name",
            name,
            role,
            "Declared filename role conflicts with Header Role.",
        )
    return None


def _filename_identity_issue(name, row):
    identity = row.get("id")
    if (
        isinstance(identity, str)
        and atom_identifier(identity) == identity
        and identity.startswith("CA-")
        and atom_identifier(name) != identity
    ):
        return (
            "file.name",
            name,
            identity,
            "Declared filename identifies a different Atom.",
        )
    return None


def _text(value: object) -> str | None:
    return None if value is None else str(value)
