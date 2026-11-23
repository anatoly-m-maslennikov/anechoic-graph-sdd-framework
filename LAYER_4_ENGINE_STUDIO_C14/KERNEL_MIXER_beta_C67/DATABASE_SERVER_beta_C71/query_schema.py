"""Report the bound Project's public query columns."""

from .table_names import ATOM_FAMILY_VIEWS, PUBLIC_NAMES

_MAIN = ("ops_ingestion_issues", *ATOM_FAMILY_VIEWS,
         *(name for old, new in PUBLIC_NAMES.items() if not new.startswith("ops_") for name in (old, new)))
_TEMP = tuple(name for old, new in PUBLIC_NAMES.items() if new.startswith("ops_") for name in (old, new))


def public_schema(connection):
    rows = connection.execute(
        "SELECT table_name, column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'main' AND ((table_catalog = current_database() "
        f"AND table_name IN {_MAIN!r}) "
        f"OR (table_catalog = 'temp' AND table_name IN {_TEMP!r})) "
        "ORDER BY table_name, ordinal_position"
    ).fetchall()
    tables = {}
    for table, name, data_type in rows:
        tables.setdefault(table, []).append({"name": name, "type": data_type})
    for table in ("atoms", "mrt_atoms", *ATOM_FAMILY_VIEWS):
        status = next((column for column in tables.get(table, []) if column["name"] == "header.state.status"), None)
        if status is not None:
            values = _status_values(connection, table)
            if values:
                status["values"] = values
    return {"tables": tables}


def _status_values(connection, table):
    rows = connection.execute(
        f'''WITH values_by_status AS (
                SELECT DISTINCT "header.state.status" AS value FROM main.{table}
                WHERE "header.state.status" IS NOT NULL
            ), sized AS (
                SELECT value, max(octet_length(encode(value))) OVER () AS max_bytes FROM values_by_status
            )
            SELECT value FROM sized WHERE max_bytes <= 1024 ORDER BY value LIMIT 257'''
    ).fetchall()
    return [row[0] for row in rows] if len(rows) <= 256 else []
