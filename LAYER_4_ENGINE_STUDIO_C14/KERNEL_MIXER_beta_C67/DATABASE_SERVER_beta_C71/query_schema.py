"""Report the bound Project's public query columns."""

_PUBLIC_TABLES = ("atoms", "native_references", "relations", "import_nodes", "module_imports", "import_edges",
                  "package_imports", "test_edges", "tested_by_edges", "import_read_issues", "package_external_imports",
                  "state_effect_findings")


def public_schema(connection):
    rows = connection.execute(
        "SELECT table_name, column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'main' AND ((table_catalog = current_database() "
        f"AND table_name IN {_PUBLIC_TABLES!r}) "
        "OR (table_catalog = 'temp' AND table_name IN ('work_journal', 'query_log'))) "
        "ORDER BY table_name, ordinal_position"
    ).fetchall()
    tables = {}
    for table, name, data_type in rows:
        tables.setdefault(table, []).append({"name": name, "type": data_type})
    status = next((column for column in tables.get("atoms", []) if column["name"] == "header.state.status"), None)
    if status is not None:
        oversized = connection.execute('SELECT EXISTS (SELECT 1 FROM main.atoms WHERE octet_length(encode("header.state.status")) > 1024)').fetchone()[0]
        if not oversized:
            values = connection.execute('SELECT DISTINCT "header.state.status" FROM main.atoms WHERE "header.state.status" IS NOT NULL ORDER BY 1 LIMIT 257').fetchall()
            if values and len(values) <= 256:
                status["values"] = [row[0] for row in values]
    return {"tables": tables}
