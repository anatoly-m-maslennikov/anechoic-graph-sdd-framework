"""Store admitted metric evidence and expose SQL analysis views."""

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.projection_sql__shared import _LARGEST, _PROFILES, _RATIOS


def snapshot_sizes(snapshot):
    if "spec_sizes" not in snapshot:
        raise ValueError("Native snapshot has no Spec size evidence")
    return snapshot["spec_sizes"]


def _validate(rows, kind):
    result, seen = [], set()
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != (
            6 if kind == "code" else 5
        ):
            raise ValueError(f"Invalid {kind} metric row")
        if kind == "code":
            unique = _validate_code(row)
        else:
            identity, full_bytes, full_lines, body_bytes, body_lines = row
            if (
                not isinstance(identity, str)
                or not identity
                or any(type(value) is not int or value < 0 for value in row[1:])
                or body_bytes > full_bytes
                or body_lines > full_lines
            ):
                raise ValueError("Invalid spec metric")
            unique = identity
        if unique in seen:
            raise ValueError(f"Duplicate {kind} metric identity")
        seen.add(unique)
        result.append(tuple(row))
    return result


def _validate_code(row):
    scope, key, identity, population, size, lines = row
    if (
        scope not in ("Component", "Package")
        or not isinstance(key, str)
        or not key
        or not isinstance(identity, str)
        or not identity
        or population
        not in (
            "implementation",
            "test_code",
            "test_assets",
            "unclassified",
        )
    ):
        raise ValueError("Invalid code metric identity or population")
    if (
        type(size) is not int
        or size < 0
        or (lines is not None and (type(lines) is not int or lines < 0))
    ):
        raise ValueError("Invalid code size")
    unique = (scope, key, identity)
    return unique


def prepare(connection):
    connection.execute(
        (
            "CREATE TABLE IF NOT EXISTS biz_architecture_code_metrics "
            "(scope_kind "
            "VARCHAR, scope_id VARCHAR, relative_path VARCHAR, population "
            "VARCHAR, bytes BIGINT, physical_lines BIGINT, PRIMARY KEY "
            "(scope_kind, scope_id, relative_path))"
        )
    )
    connection.execute(
        (
            "CREATE TABLE IF NOT EXISTS biz_architecture_spec_metrics "
            "(atom_ref "
            "VARCHAR PRIMARY KEY, full_bytes BIGINT, full_lines BIGINT, "
            "body_bytes BIGINT, body_lines BIGINT)"
        )
    )
    connection.execute(
        (
            "CREATE TABLE IF NOT EXISTS "
            "mrt_real_graph_package_spec_bindings "
            "(package_key VARCHAR, atom_ref VARCHAR, "
            "PRIMARY KEY (package_key, "
            "atom_ref))"
        )
    )
    connection.execute(_RATIOS)
    connection.execute(_LARGEST)
    connection.execute(_PROFILES)


def drop(connection):
    for view in (
        "biz_architecture_ratios",
        "biz_package_review_profiles",
        "biz_package_largest_files",
    ):
        connection.execute(f"DROP VIEW IF EXISTS {view}")
    for table in (
        "biz_architecture_code_metrics",
        "biz_architecture_spec_metrics",
        "mrt_real_graph_package_spec_bindings",
    ):
        connection.execute(f"DROP TABLE IF EXISTS {table}")


def _insert_rows(connection, table, rows, types):
    if rows:
        columns = ", ".join(f"unnest(?::{kind}[])" for kind in types)
        connection.execute(
            f"INSERT INTO {table} SELECT {columns}",
            [list(column) for column in zip(*rows, strict=False)],
        )


def replace_code(connection, rows):
    """Replace code evidence within the caller's transaction."""
    rows = _validate(rows, "code")
    connection.execute("DELETE FROM biz_architecture_code_metrics")
    _insert_rows(
        connection,
        "biz_architecture_code_metrics",
        rows,
        ("VARCHAR", "VARCHAR", "VARCHAR", "VARCHAR", "BIGINT", "BIGINT"),
    )


def replace_spec(connection, rows):
    """Replace spec evidence within the caller's transaction."""
    rows = _validate(rows, "spec")
    connection.execute("DELETE FROM biz_architecture_spec_metrics")
    _insert_rows(
        connection,
        "biz_architecture_spec_metrics",
        rows,
        ("VARCHAR", "BIGINT", "BIGINT", "BIGINT", "BIGINT"),
    )


def apply_spec_delta(connection, old_exact_refs, rows):
    """Replace only the admitted Atom sizes named by a native delta."""
    rows = _validate(rows, "spec")
    refs = list(old_exact_refs)
    if any(not isinstance(ref, str) or not ref for ref in refs) or len(
        set(refs)
    ) != len(refs):
        raise ValueError("Invalid or duplicate old exact reference")
    if not refs and not rows:
        return
    conflict = connection.execute(
        """SELECT EXISTS (
            SELECT 1 FROM biz_architecture_spec_metrics
            WHERE atom_ref IN (SELECT unnest(?::VARCHAR[]))
              AND atom_ref NOT IN (SELECT unnest(?::VARCHAR[]))
        )""",
        [[row[0] for row in rows], refs],
    ).fetchone()[0]
    if conflict:
        raise ValueError("Spec delta conflicts with an existing Atom")
    if refs:
        connection.execute(
            (
                "DELETE FROM biz_architecture_spec_metrics WHERE atom_ref IN "
                "(SELECT unnest(?::VARCHAR[]))"
            ),
            [refs],
        )
    _insert_rows(
        connection,
        "biz_architecture_spec_metrics",
        rows,
        ("VARCHAR", "BIGINT", "BIGINT", "BIGINT", "BIGINT"),
    )


def replace_bindings(connection, rows):
    """Replace graph-owned exact package-to-Atom bindings."""
    result, seen = [], set()
    for row in rows:
        if (
            not isinstance(row, (list, tuple))
            or len(row) != 2
            or any(not isinstance(value, str) or not value for value in row)
        ):
            raise ValueError("Invalid package binding")
        pair = tuple(row)
        if pair in seen:
            raise ValueError("Duplicate package binding")
        seen.add(pair)
        result.append(pair)
    connection.execute("DELETE FROM mrt_real_graph_package_spec_bindings")
    _insert_rows(
        connection,
        "mrt_real_graph_package_spec_bindings",
        result,
        ("VARCHAR", "VARCHAR"),
    )
