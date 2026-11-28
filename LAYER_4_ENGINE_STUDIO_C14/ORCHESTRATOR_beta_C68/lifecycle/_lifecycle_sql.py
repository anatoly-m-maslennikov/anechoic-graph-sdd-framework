"""Build generation-pinned Lifecycle SQL from checked selectors."""

import re


_ALLOCATION_REFERENCES = """
    SELECT reference FROM main.atoms {archive_refs}
    UNION ALL
    SELECT atom_ref FROM main.ops_ingestion_issues WHERE source IN ('atom', 'archive')
        AND regexp_full_match(atom_ref, '[A-Z][A-Z0-9]*-[TS]-[0-9]{{1,255}}(?:@[1-9][0-9]*(?:-draft)?)?')
    UNION ALL
    SELECT regexp_extract(relative_path,
        '(?:^|/)([A-Z][A-Z0-9]*-[TS]-[0-9]{{1,255}})(?:@[1-9][0-9]*(?:-draft)?)?[-.][^/]*[.]md$', 1)
    FROM main.ops_ingestion_issues WHERE source IN ('atom', 'archive')
"""

_SQL = """WITH RECURSIVE
    native AS (
      SELECT a.reference AS ref, n.exact_ref AS exact_ref,
        split_part(n.exact_ref, '@', 1) AS id,
        CASE WHEN a.relative_path = '.' THEN a.filename ELSE a.relative_path || '/' || a.filename END AS path,
        a."header.state.version" AS version, a."header.state.status" AS status, a.status_group,
        r.target_kind AS owner_kind, r.target_ref AS owner_ref
      FROM main.atoms a JOIN main.native_references n ON a.reference=n.reference
      LEFT JOIN main.relations r ON r.source_kind='Atom' AND r.source_ref=a.reference
        AND r.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') AND NOT r.derived
    ),
    owners(id) AS (
      SELECT id FROM (SELECT {owner_lit} AS id WHERE {owner_lit} <> ''
        UNION SELECT n.owner_ref FROM native n WHERE n.id={target_lit}
          AND n.owner_kind='Atom' AND (n.ref={exact_lit} OR n.status_group='Current'))
      UNION SELECT n.owner_ref FROM native n JOIN owners o ON n.id=o.id
        WHERE n.owner_kind='Atom' AND (n.status_group='Current' OR (n.status_group='Draft' AND n.version=1))
    ),
    selected AS (
      SELECT DISTINCT n.*, (n.id={target_lit} AND (n.ref={exact_lit} OR n.status_group='Current')
          OR n.id IN (SELECT id FROM owners) AND (n.status_group='Current' OR (n.status_group='Draft' AND n.version=1))
          OR n.id IN {sources} AND n.status_group='Current'
          OR n.ref IN (SELECT source_ref FROM main.relations WHERE relation_type='IS_REPLACEMENT_FOR'
              AND NOT derived AND target_ref={target_lit}) AND n.status_group='Current') AS should_read
      FROM native n WHERE n.id={target_lit} OR n.id IN (SELECT id FROM owners)
        OR n.id IN {sources} AND n.status_group='Current'
        OR n.ref IN (SELECT source_ref FROM main.relations WHERE relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY')
            AND NOT derived AND target_kind='Atom' AND target_ref={target_lit})
        OR n.ref IN (SELECT source_ref FROM main.relations WHERE relation_type='IS_REPLACEMENT_FOR'
            AND NOT derived AND target_ref={target_lit}) AND n.status_group='Current'
    ),
    allocation_refs AS ({allocation_refs}),
    numbers AS (
      SELECT regexp_extract(reference, '^{prefix}-([TS])-([0-9]+)(@|$)', 1) AS family,
        ltrim(regexp_extract(reference, '^{prefix}-([TS])-([0-9]+)(@|$)', 2), '0') AS number
      FROM allocation_refs WHERE {numbers} AND starts_with(reference, '{prefix}-')
    ),
    SELECT g.id, g.structure, {model_sql}, json_extract(g.model, '$.ticket_labels')::VARCHAR,
      coalesce((SELECT arg_max(number, (length(number), number)) FROM numbers WHERE family='T' AND number<>''), '0'),
      coalesce((SELECT arg_max(number, (length(number), number)) FROM numbers WHERE family='S' AND number<>''), '0'),
      coalesce((SELECT to_json(list(struct_pack(ref := ref, _exact_ref := exact_ref, source_path := path,
        version := version, status := status, status_group := status_group,
        id := id, owner_kind := owner_kind, owner_ref := owner_ref, read := should_read)))::VARCHAR
        FROM selected), '[]'),
      EXISTS(SELECT 1 FROM main.relations WHERE relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') AND NOT derived
        AND target_kind='Atom' AND target_ref={target_lit}) OR EXISTS(SELECT 1 FROM native parent JOIN native child
        ON starts_with(child.path, regexp_replace(parent.path, '[.]md$', '') || '/')
        WHERE parent.id={target_lit} AND (parent.ref={exact_lit} OR parent.status_group='Current')), 
      coalesce((SELECT to_json(list(DISTINCT lens))::VARCHAR FROM main.lifecycle_lenses WHERE lens IS NOT NULL), '[]'),
      {archive_version} AS max_archived_version
    FROM main.int_lifecycle_generation g"""


def _literal(value):
    return "'" + value.replace("'", "''") + "'"


def _allocation_references(archive_versions):
    archive_refs = (
        """WHERE status_group <> 'Archived'
        UNION ALL SELECT atom_id FROM main.ops_archive_versions"""
        if archive_versions
        else ""
    )
    return _ALLOCATION_REFERENCES.format(archive_refs=archive_refs)


def lifecycle_sql(prefix, name, arguments, *, archive_versions=False):
    """Build a single SELECT so every returned value belongs to one generation."""
    if not isinstance(prefix, str) or not re.fullmatch(
        r"[A-Z][A-Z0-9]*", prefix
    ):
        raise ValueError("Invalid Project prefix")
    target, owner, new, container = _selectors(name, arguments)
    target_id = target.split("@", 1)[0]
    target_lit, exact_lit, owner_lit = map(
        _literal, (target_id, target, owner)
    )
    is_create = (
        name in {"atom_lifecycle_create_draft", "atom_lifecycle_create_asset"}
        and isinstance(new, dict)
        and bool(new)
    )
    sources = (
        "('AN-S-1928','AN-S-1834','AN-S-1831')"
        if name == "atom_lifecycle_change_status"
        else "('')"
    )
    numbers = "TRUE" if is_create else "FALSE"
    needs_model = _include_model(name, new, container, is_create, target_id)
    model_sql = (
        'json_merge_patch(g.model::JSON, \'{"declarations":null,"ticket_labels":null}\')::VARCHAR'
        if needs_model
        else "NULL"
    )
    archive_version = (
        f"COALESCE((SELECT max_version FROM main.ops_archive_versions WHERE atom_id={target_lit}), 0)::VARCHAR"
        if archive_versions
        else "'0'"
    )
    return _SQL.format(
        prefix=prefix,
        target_lit=target_lit,
        exact_lit=exact_lit,
        owner_lit=owner_lit,
        sources=sources,
        numbers=numbers,
        model_sql=model_sql,
        allocation_refs=_allocation_references(archive_versions),
        archive_version=archive_version,
    )


def _selectors(name, arguments):
    if not isinstance(name, str) or not isinstance(arguments, dict):
        raise ValueError("Invalid lifecycle query arguments")
    target = arguments.get("target", arguments.get("sourceCurrent", {}))
    target = target.get("ref_id", "") if isinstance(target, dict) else ""
    new = arguments.get("newAtom", {})
    container = new.get("container", {}) if isinstance(new, dict) else {}
    owner = container.get("atom", "") if isinstance(container, dict) else ""
    if not isinstance(target, str) or not isinstance(owner, str):
        raise ValueError("Invalid lifecycle selector")
    return target, owner, new, container


def _include_model(name, new, container, is_create, target_id):
    template = new.get("template") if isinstance(new, dict) else None
    return (
        is_create
        and name == "atom_lifecycle_create_draft"
        and isinstance(template, str)
        and template not in {"task", "epic"}
        and container == {"component": "C00"}
        or "-S-" in target_id
        and name
        in {"atom_lifecycle_promote_draft", "atom_lifecycle_change_status"}
    )
