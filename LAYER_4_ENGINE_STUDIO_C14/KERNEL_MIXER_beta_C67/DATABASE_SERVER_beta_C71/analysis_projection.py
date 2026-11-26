"""Store admitted metric evidence and expose SQL analysis views."""

def snapshot_sizes(snapshot):
    if "spec_sizes" not in snapshot:
        raise ValueError("Native snapshot has no Spec size evidence")
    return snapshot["spec_sizes"]



def _validate(rows, kind):
    result, seen = [], set()
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != (6 if kind == 'code' else 5):
            raise ValueError(f'Invalid {kind} metric row')
        if kind == 'code':
            scope, key, identity, population, size, lines = row
            if (scope not in ('Component', 'Package') or not isinstance(key, str) or not key
                    or not isinstance(identity, str) or not identity or population not in
                    ('implementation', 'test_code', 'test_assets', 'unclassified')):
                raise ValueError('Invalid code metric identity or population')
            if type(size) is not int or size < 0 or (lines is not None and (type(lines) is not int or lines < 0)):
                raise ValueError('Invalid code size')
            unique = (scope, key, identity)
        else:
            identity, full_bytes, full_lines, body_bytes, body_lines = row
            if (not isinstance(identity, str) or not identity
                    or any(type(value) is not int or value < 0 for value in row[1:])
                    or body_bytes > full_bytes or body_lines > full_lines):
                raise ValueError('Invalid spec metric')
            unique = identity
        if unique in seen:
            raise ValueError(f'Duplicate {kind} metric identity')
        seen.add(unique)
        result.append(tuple(row))
    return result


def prepare(connection):
    connection.execute('CREATE TABLE IF NOT EXISTS biz_architecture_code_metrics (scope_kind VARCHAR, scope_id VARCHAR, relative_path VARCHAR, population VARCHAR, bytes BIGINT, physical_lines BIGINT, PRIMARY KEY (scope_kind, scope_id, relative_path))')
    connection.execute('CREATE TABLE IF NOT EXISTS biz_architecture_spec_metrics (atom_ref VARCHAR PRIMARY KEY, full_bytes BIGINT, full_lines BIGINT, body_bytes BIGINT, body_lines BIGINT)')
    connection.execute('CREATE TABLE IF NOT EXISTS mrt_real_graph_package_spec_bindings (package_key VARCHAR, atom_ref VARCHAR, PRIMARY KEY (package_key, atom_ref))')
    connection.execute(_RATIOS)
    connection.execute(_LARGEST)
    connection.execute(_PROFILES)


def drop(connection):
    for view in ("biz_architecture_ratios", "biz_package_review_profiles", "biz_package_largest_files"):
        connection.execute(f"DROP VIEW IF EXISTS {view}")
    for table in ("biz_architecture_code_metrics", "biz_architecture_spec_metrics", "mrt_real_graph_package_spec_bindings"):
        connection.execute(f"DROP TABLE IF EXISTS {table}")


def _insert_rows(connection, table, rows, types):
    if rows:
        columns = ', '.join(f'unnest(?::{kind}[])' for kind in types)
        connection.execute(f'INSERT INTO {table} SELECT {columns}', [list(column) for column in zip(*rows)])


def replace_code(connection, rows):
    """Replace code evidence within the caller's transaction."""
    rows = _validate(rows, 'code')
    connection.execute('DELETE FROM biz_architecture_code_metrics')
    _insert_rows(connection, 'biz_architecture_code_metrics', rows, ('VARCHAR', 'VARCHAR', 'VARCHAR', 'VARCHAR', 'BIGINT', 'BIGINT'))


def replace_spec(connection, rows):
    """Replace spec evidence within the caller's transaction."""
    rows = _validate(rows, 'spec')
    connection.execute('DELETE FROM biz_architecture_spec_metrics')
    _insert_rows(connection, 'biz_architecture_spec_metrics', rows, ('VARCHAR', 'BIGINT', 'BIGINT', 'BIGINT', 'BIGINT'))


def apply_spec_delta(connection, old_exact_refs, rows):
    """Replace only the admitted Atom sizes named by a native delta."""
    rows = _validate(rows, 'spec')
    refs = list(old_exact_refs)
    if any(not isinstance(ref, str) or not ref for ref in refs) or len(set(refs)) != len(refs):
        raise ValueError('Invalid or duplicate old exact reference')
    if not refs and not rows:
        return
    conflict = connection.execute(
        """SELECT EXISTS (
            SELECT 1 FROM biz_architecture_spec_metrics
            WHERE atom_ref IN (SELECT unnest(?::VARCHAR[]))
              AND atom_ref NOT IN (SELECT unnest(?::VARCHAR[]))
        )""", [[row[0] for row in rows], refs],
    ).fetchone()[0]
    if conflict:
        raise ValueError('Spec delta conflicts with an existing Atom')
    if refs:
        connection.execute('DELETE FROM biz_architecture_spec_metrics WHERE atom_ref IN (SELECT unnest(?::VARCHAR[]))', [refs])
    _insert_rows(connection, 'biz_architecture_spec_metrics', rows, ('VARCHAR', 'BIGINT', 'BIGINT', 'BIGINT', 'BIGINT'))


def replace_bindings(connection, rows):
    """Replace graph-owned exact package-to-Atom bindings."""
    result, seen = [], set()
    for row in rows:
        if (not isinstance(row, (list, tuple)) or len(row) != 2
                or any(not isinstance(value, str) or not value for value in row)):
            raise ValueError('Invalid package binding')
        pair = tuple(row)
        if pair in seen:
            raise ValueError('Duplicate package binding')
        seen.add(pair)
        result.append(pair)
    connection.execute('DELETE FROM mrt_real_graph_package_spec_bindings')
    _insert_rows(connection, 'mrt_real_graph_package_spec_bindings', result, ('VARCHAR', 'VARCHAR'))


_RATIOS = """CREATE OR REPLACE VIEW biz_architecture_ratios AS
WITH RECURSIVE ancestry AS (
 SELECT n.exact_ref, r.target_kind, r.target_ref FROM main.mrt_atom_references n JOIN main.mrt_atom_graph_relations r
 ON r.source_kind='Atom' AND r.source_ref=n.reference
 WHERE r.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') AND NOT r.derived
 UNION SELECT a.exact_ref, r.target_kind, r.target_ref FROM ancestry a JOIN main.mrt_atom_graph_relations r
 ON a.target_kind='Atom' AND r.source_kind='Atom' AND r.source_ref=a.target_ref
 WHERE r.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') AND NOT r.derived),
component_atoms AS (SELECT DISTINCT exact_ref, target_ref AS component_id FROM ancestry WHERE target_kind='Component'),
scopes AS (SELECT scope_kind, scope_id FROM biz_architecture_code_metrics
 UNION SELECT 'Component', component_id FROM component_atoms JOIN biz_architecture_spec_metrics ON exact_ref=atom_ref
 UNION SELECT 'Package', package_key FROM mrt_real_graph_package_spec_bindings),
code AS (SELECT scope_kind, scope_id,
 sum(bytes) FILTER (WHERE population='implementation') AS impl_bytes,
 sum(physical_lines) FILTER (WHERE population='implementation') AS impl_lines,
 count(*) FILTER (WHERE population='implementation' AND physical_lines IS NULL) AS impl_unknown,
 sum(bytes) FILTER (WHERE population='test_code') AS test_bytes,
 sum(physical_lines) FILTER (WHERE population='test_code') AS test_lines,
 count(*) FILTER (WHERE population='test_code' AND physical_lines IS NULL) AS test_unknown,
 sum(bytes) FILTER (WHERE population IN ('implementation','test_code')) AS combined_bytes,
 sum(physical_lines) FILTER (WHERE population IN ('implementation','test_code')) AS combined_lines,
 count(*) FILTER (WHERE population IN ('implementation','test_code') AND physical_lines IS NULL) AS combined_unknown,
 coalesce(sum(bytes) FILTER (WHERE population='test_assets'),0) AS test_assets_bytes,
 sum(physical_lines) FILTER (WHERE population='test_assets') AS test_assets_lines,
 count(*) FILTER (WHERE population='test_assets' AND physical_lines IS NULL) AS test_assets_unknown_lines,
 coalesce(sum(bytes) FILTER (WHERE population='unclassified'),0) AS unclassified_bytes,
 sum(physical_lines) FILTER (WHERE population='unclassified') AS unclassified_lines,
 count(*) FILTER (WHERE population='unclassified' AND physical_lines IS NULL) AS unclassified_unknown_lines
 FROM biz_architecture_code_metrics GROUP BY 1,2),
bound AS (SELECT b.package_key, b.atom_ref, count(*) OVER (PARTITION BY b.atom_ref) > 1 AS shared
 FROM mrt_real_graph_package_spec_bindings b),
spec_rows AS (SELECT 'Component' AS scope_kind, c.component_id AS scope_id, a.atom_ref,
 a.full_bytes, a.full_lines, a.body_bytes, a.body_lines, false AS shared
 FROM component_atoms c JOIN biz_architecture_spec_metrics a ON c.exact_ref=a.atom_ref
 UNION ALL SELECT 'Package', b.package_key, b.atom_ref, a.full_bytes, a.full_lines, a.body_bytes, a.body_lines, b.shared
 FROM bound b JOIN biz_architecture_spec_metrics a USING (atom_ref)),
spec AS (SELECT scope_kind, scope_id, sum(full_bytes) FILTER (WHERE NOT shared) AS full_bytes,
 sum(full_lines) FILTER (WHERE NOT shared) AS full_lines, sum(body_bytes) FILTER (WHERE NOT shared) AS body_bytes,
 sum(body_lines) FILTER (WHERE NOT shared) AS body_lines, count(*) AS spec_atoms,
 count(*) FILTER (WHERE shared) AS shared_atoms
 FROM spec_rows GROUP BY 1,2),
measures AS (SELECT s.scope_kind, s.scope_id, c.*, p.* EXCLUDE (scope_kind, scope_id),
 code_population, spec_population,
 CASE WHEN code_population='implementation' THEN coalesce(impl_bytes,0)
 WHEN code_population='test_code' THEN coalesce(test_bytes,0) ELSE coalesce(combined_bytes,0) END AS numerator_bytes,
 CASE WHEN code_population='implementation' THEN CASE WHEN coalesce(impl_unknown,0)>0 THEN NULL ELSE coalesce(impl_lines,0) END
 WHEN code_population='test_code' THEN CASE WHEN coalesce(test_unknown,0)>0 THEN NULL ELSE coalesce(test_lines,0) END
 ELSE CASE WHEN coalesce(combined_unknown,0)>0 THEN NULL ELSE coalesce(combined_lines,0) END END AS numerator_lines,
 CASE WHEN spec_population='full' THEN coalesce(full_bytes,0) ELSE coalesce(body_bytes,0) END AS denominator_bytes,
 CASE WHEN spec_population='full' THEN coalesce(full_lines,0) ELSE coalesce(body_lines,0) END AS denominator_lines
 FROM scopes s LEFT JOIN code c USING (scope_kind,scope_id) LEFT JOIN spec p USING (scope_kind,scope_id)
 CROSS JOIN (VALUES ('implementation'),('test_code'),('implementation_and_test_code')) cp(code_population)
 CROSS JOIN (VALUES ('full'),('body')) sp(spec_population))
SELECT scope_kind, scope_id, code_population, spec_population, numerator_bytes, denominator_bytes,
 numerator_lines, denominator_lines, numerator_bytes / nullif(denominator_bytes,0) AS bytes_ratio,
 numerator_lines / nullif(denominator_lines,0) AS lines_ratio,
 numerator_bytes / 1000.0 AS numerator_kb, denominator_bytes / 1000.0 AS denominator_kb,
 numerator_bytes / 1000000.0 AS numerator_mb, denominator_bytes / 1000000.0 AS denominator_mb,
 CASE WHEN coalesce(shared_atoms,0)>0 THEN 'partial' WHEN coalesce(spec_atoms,0)>0 THEN 'bound'
 ELSE 'unbound' END AS spec_status,
 coalesce(shared_atoms,0)>0 AS partial_spec, coalesce(shared_atoms,0) AS shared_atoms,
 coalesce(test_assets_bytes,0) AS test_assets_bytes, test_assets_lines, coalesce(test_assets_unknown_lines,0) AS test_assets_unknown_lines,
 coalesce(unclassified_bytes,0) AS unclassified_bytes, unclassified_lines, coalesce(unclassified_unknown_lines,0) AS unclassified_unknown_lines
 FROM measures"""

_LARGEST = """CREATE OR REPLACE VIEW biz_package_largest_files AS
SELECT scope_id AS package_key, relative_path, bytes, physical_lines,
 row_number() OVER (PARTITION BY scope_id ORDER BY bytes DESC, relative_path) AS size_rank
 FROM biz_architecture_code_metrics WHERE scope_kind='Package' AND population='implementation'"""

_PROFILES = """CREATE OR REPLACE VIEW biz_package_review_profiles AS
WITH sizes AS (SELECT scope_id AS package_key, sum(bytes) AS implementation_bytes,
 CASE WHEN count(*) FILTER (WHERE physical_lines IS NULL)>0 THEN NULL ELSE sum(physical_lines) END AS implementation_lines,
 count(*) AS implementation_file_count, max(bytes) AS largest_file_bytes
 FROM biz_architecture_code_metrics WHERE scope_kind='Package' AND population='implementation' GROUP BY scope_id),
 imports AS (SELECT source_key AS package_key, count(*) AS outgoing_packages, sum(occurrence_count) AS outgoing_occurrences FROM mrt_real_graph_package_imports GROUP BY source_key),
 incoming AS (SELECT target_key AS package_key, count(*) AS incoming_packages, sum(occurrence_count) AS incoming_occurrences FROM mrt_real_graph_package_imports GROUP BY target_key)
SELECT s.*, rank() OVER (ORDER BY implementation_bytes DESC) AS size_rank,
 percent_rank() OVER (ORDER BY implementation_bytes) AS size_percent_rank,
 coalesce(i.outgoing_packages,0) AS outgoing_packages, coalesce(i.outgoing_occurrences,0) AS outgoing_occurrences,
 coalesce(n.incoming_packages,0) AS incoming_packages, coalesce(n.incoming_occurrences,0) AS incoming_occurrences
 FROM sizes s LEFT JOIN imports i USING (package_key) LEFT JOIN incoming n USING (package_key)"""
