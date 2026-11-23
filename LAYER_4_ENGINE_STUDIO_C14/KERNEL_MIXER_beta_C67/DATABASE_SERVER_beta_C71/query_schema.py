"""Report the bound Project's public query columns."""

from .table_names import ATOM_FAMILY_VIEWS, PUBLIC_NAMES

_MAIN = (*ATOM_FAMILY_VIEWS,
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
    field = '"header.state.status"'
    oversized = connection.execute(
        f"SELECT EXISTS (SELECT 1 FROM main.{table} WHERE octet_length(encode({field})) > 1024)"
    ).fetchone()[0]
    if oversized:
        return []
    rows = connection.execute(
        f"SELECT DISTINCT {field} FROM main.{table} WHERE {field} IS NOT NULL ORDER BY 1 LIMIT 257"
    ).fetchall()
    return [row[0] for row in rows] if len(rows) <= 256 else []
