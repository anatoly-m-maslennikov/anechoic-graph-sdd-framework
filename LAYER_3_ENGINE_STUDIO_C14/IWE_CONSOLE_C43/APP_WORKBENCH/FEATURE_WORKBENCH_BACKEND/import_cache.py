"""Persist raw import scans on the Workbench connection."""

from __future__ import annotations

from ..FEATURE_IMPORT_GRAPH_C61.source import ImportSite, Source


# Increment when the stored schema or parser semantics change.
_CACHE_VERSION = 2
_SCHEMA = "_anechoic_import_cache"


def _exists(connection) -> bool:
    return bool(connection.execute(
        "SELECT count(*) FROM information_schema.schemata WHERE catalog_name = current_database() AND schema_name = ?", [_SCHEMA]
    ).fetchone()[0])


def _compatible(connection) -> bool:
    return connection.execute(f"SELECT version FROM {_SCHEMA}.version").fetchall() == [(_CACHE_VERSION,)]


def read_import_sources(connection) -> dict[str, Source]:
    """Return a compatible snapshot, or an empty one when none exists."""
    if not _exists(connection) or not _compatible(connection):
        return {}
    sites: dict[str, list[ImportSite]] = {}
    for path, module, name, level, line, column in connection.execute(
        f'SELECT path, module, name, level, line, "column" FROM {_SCHEMA}.sites ORDER BY path, ordinal'
    ).fetchall():
        sites.setdefault(path, []).append(ImportSite(module, name, level, line, column))
    return {
        path: Source(language, status, signature, tuple(sites.get(path, ())), error_message)
        for path, language, status, signature, error_message in connection.execute(
            f"SELECT path, language, status, signature, error_message FROM {_SCHEMA}.sources"
        ).fetchall()
    }


def clear_import_sources(connection) -> None:
    """Remove the snapshot inside the caller's transaction."""
    connection.execute(f"DROP SCHEMA IF EXISTS {_SCHEMA} CASCADE")


def replace_import_sources(connection, sources: dict[str, Source],
                           previous: dict[str, Source] | None = None) -> None:
    """Replace the snapshot inside the caller's transaction."""
    if _exists(connection) and not _compatible(connection):
        clear_import_sources(connection)
        previous = {}
    if not _exists(connection):
        previous = {}
        connection.execute(f"CREATE SCHEMA {_SCHEMA}")
        connection.execute(f"CREATE TABLE {_SCHEMA}.version (version INTEGER NOT NULL)")
        connection.execute(f"INSERT INTO {_SCHEMA}.version VALUES (?)", [_CACHE_VERSION])
        connection.execute(
            f"CREATE TABLE {_SCHEMA}.sources (path VARCHAR PRIMARY KEY, language VARCHAR NOT NULL, "
            "status VARCHAR NOT NULL, signature VARCHAR NOT NULL, error_message VARCHAR)"
        )
        connection.execute(
            f'CREATE TABLE {_SCHEMA}.sites (path VARCHAR NOT NULL, ordinal INTEGER NOT NULL, '
            'module VARCHAR NOT NULL, name VARCHAR, level INTEGER NOT NULL, line INTEGER NOT NULL, '
            '"column" INTEGER NOT NULL, PRIMARY KEY (path, ordinal))'
        )
    if previous is None:
        previous = read_import_sources(connection)
    changed = {path for path in sources.keys() | previous.keys()
               if sources.get(path) != previous.get(path)}
    if not changed:
        return
    for table in ("sites", "sources"):
        connection.execute(f"DELETE FROM {_SCHEMA}.{table} WHERE path IN (SELECT unnest(?))", [list(changed)])
    rows = [(path, source.language, source.status, source.signature, source.error_message)
            for path, source in sources.items() if path in changed]
    if rows:
        connection.execute(f"INSERT INTO {_SCHEMA}.sources SELECT unnest(?), unnest(?), unnest(?), unnest(?), unnest(?)",
                           [list(column) for column in zip(*rows, strict=True)])
    rows = [(path, ordinal, site.module, site.name, site.level, site.line, site.column)
            for path, source in sources.items() if path in changed
            for ordinal, site in enumerate(source.imports)]
    if rows:
        connection.execute(f"INSERT INTO {_SCHEMA}.sites SELECT unnest(?), unnest(?), unnest(?), "
                           "unnest(?), unnest(?), unnest(?), unnest(?)",
                           [list(column) for column in zip(*rows, strict=True)])
