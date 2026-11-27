"""Select generation-pinned lifecycle context from the private database."""
from contextlib import closing
import json
from pathlib import PurePosixPath
import re

from .jobs import UnixConnection


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

_SQL = '''WITH RECURSIVE
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
    FROM main.int_lifecycle_generation g'''

def _literal(value):
    return "'" + value.replace("'", "''") + "'"


def _allocation_references(archive_versions):
    archive_refs = ("""WHERE status_group <> 'Archived'
        UNION ALL SELECT atom_id FROM main.ops_archive_versions""" if archive_versions else "")
    return _ALLOCATION_REFERENCES.format(archive_refs=archive_refs)


def lifecycle_sql(prefix, name, arguments, *, archive_versions=False):
    """Build a single SELECT so every returned value belongs to one generation."""
    if not isinstance(prefix, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix):
        raise ValueError("Invalid Project prefix")
    if not isinstance(name, str) or not isinstance(arguments, dict):
        raise ValueError("Invalid lifecycle query arguments")
    target = arguments.get('target', arguments.get('sourceCurrent', {}))
    target = target.get('ref_id', '') if isinstance(target, dict) else ''
    new = arguments.get('newAtom', {})
    container = new.get('container', {}) if isinstance(new, dict) else {}
    owner = container.get('atom', '') if isinstance(container, dict) else ''
    if not isinstance(target, str) or not isinstance(owner, str):
        raise ValueError("Invalid lifecycle selector")
    target_id = target.split('@', 1)[0]
    target_lit, exact_lit, owner_lit = map(_literal, (target_id, target, owner))
    is_create = name in {'atom_lifecycle_create_draft', 'atom_lifecycle_create_asset'} and isinstance(new, dict) and bool(new)
    sources = "('AN-S-1928','AN-S-1834','AN-S-1831')" if name == 'atom_lifecycle_change_status' else "('')"
    numbers = "TRUE" if is_create else "FALSE"
    template = new.get('template') if isinstance(new, dict) else None
    needs_model = (is_create and name == 'atom_lifecycle_create_draft'
                   and isinstance(template, str) and template not in {'task', 'epic'}
                   and container == {'component': 'C00'}
                   or '-S-' in target_id and name in {'atom_lifecycle_promote_draft', 'atom_lifecycle_change_status'})
    model_sql = "json_merge_patch(g.model::JSON, '{\"declarations\":null,\"ticket_labels\":null}')::VARCHAR" if needs_model else 'NULL'
    archive_version = (f"COALESCE((SELECT max_version FROM main.ops_archive_versions WHERE atom_id={target_lit}), 0)::VARCHAR"
                       if archive_versions else "'0'")
    return _SQL.format(prefix=prefix, target_lit=target_lit, exact_lit=exact_lit, owner_lit=owner_lit,
                       sources=sources, numbers=numbers, model_sql=model_sql,
                       allocation_refs=_allocation_references(archive_versions), archive_version=archive_version)


def ticket_allocation(socket_path, instance_id, base_generation, prefix, *, archive_versions=False):
    if re.fullmatch(r"[A-Z][A-Z0-9]*", prefix) is None:
        raise ValueError("Invalid Project prefix")
    sql = f"""WITH allocation_refs AS ({_allocation_references(archive_versions)}), numbers AS (
        SELECT ltrim(regexp_extract(reference, '^{prefix}-T-([0-9]+)(@|$)', 1), '0') AS number
        FROM allocation_refs WHERE starts_with(reference, '{prefix}-T-')
    )
    SELECT id, coalesce(nullif((SELECT arg_max(number, (length(number), number)) FROM numbers), ''), '0'),
        json_extract(model, '$.ticket_labels')::VARCHAR
    FROM main.int_lifecycle_generation"""
    rows = _query_rows(socket_path, instance_id, sql, "Ticket allocation")
    if (not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], list)
            or len(rows[0]) != 3 or rows[0][0] != base_generation):
        raise ValueError("Kernel generation changed before Ticket allocation")
    number = rows[0][1]
    if not isinstance(number, str) or re.fullmatch(r"0|[1-9][0-9]*", number) is None:
        raise ValueError("Kernel returned an invalid Ticket number")
    if rows[0][2] is None:
        raise ValueError("The admitted Model lacks Ticket label rules")
    labels = json.loads(rows[0][2])
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        raise ValueError("Kernel returned invalid Ticket label rules")
    return number, labels


def _query_rows(socket_path, instance_id, sql, purpose):
    request = json.dumps({'instance_id': instance_id, 'sql': sql})
    with closing(UnixConnection(socket_path)) as connection:
        connection.request('POST', '/database', request, {'Content-Type': 'application/json'})
        response = connection.getresponse()
        payload = json.loads(response.read())
        if response.status != 200:
            message = payload.get('error', {}).get('message', 'query failed')
            raise ValueError(f"Kernel refused {purpose}: {str(message)[:1024]}")
        return payload['result']['rows']


def archive_versions_available(socket_path, instance_id):
    sql = """SELECT EXISTS (SELECT 1 FROM duckdb_tables() WHERE database_name=current_database()
        AND schema_name='main' AND table_name='ops_archive_versions')"""
    return _query_rows(socket_path, instance_id, sql, "Archive version checkpoint") == [[True]]


def lifecycle_context(socket_path, instance_id, base, prefix, name, arguments, *, archive_versions=False):
    sql = lifecycle_sql(prefix, name, arguments, archive_versions=archive_versions)
    rows = _query_rows(socket_path, instance_id, sql, "lifecycle context query")
    if not isinstance(rows, list) or len(rows) != 1 or len(rows[0]) != 10 or rows[0][0] != base:
        raise ValueError('Kernel generation changed before lifecycle context query')
    _, structure, model, labels, ticket, spec, carriers, descendants, lenses, archived_version = rows[0]
    model = json.loads(model) if model is not None else None
    structure, labels, carriers, lenses = map(json.loads, (structure, labels, carriers, lenses))
    if (not isinstance(structure, dict) or model is not None and not isinstance(model, dict) or not isinstance(labels, list)
            or not all(isinstance(x, str) for x in labels) or not isinstance(carriers, list)
            or not isinstance(lenses, list) or not all(isinstance(x, str) for x in lenses)
            or type(descendants) is not bool
            or any(not isinstance(x, str) or not re.fullmatch(r'0|[1-9][0-9]*', x)
                   for x in (ticket, spec, archived_version))):
        raise ValueError('Kernel returned invalid lifecycle context')
    return {'structure': structure, 'model': model, 'ticket_labels': labels, 'max_numbers': {'T': ticket, 'S': spec},
            'carriers': carriers, 'has_descendants': descendants, 'lenses': lenses,
            'max_archived_version': int(archived_version)}


def requires_project_capture(job, context, control):
    target = job.arguments.get("target")
    ref = target.get("ref_id") if isinstance(target, dict) else None
    operation = job.name
    if not isinstance(ref, str):
        return False
    if "-T-" in ref:
        return context["has_descendants"] and operation in {
            "atom_lifecycle_promote_draft", "atom_lifecycle_change_status",
        }
    if operation not in {"atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive"}:
        return False
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        is_ontology_model_source, ontology_component_path,
    )

    atom_id = ref.partition("@")[0]
    archiving_spec = "-S-" in atom_id and (operation == "atom_lifecycle_archive"
        or (operation == "atom_lifecycle_change_status" and job.arguments.get("targetStatus") == "archived"))
    control_path = PurePosixPath(control)
    custom = {PurePosixPath(directory, "CUSTOM_MODEL")
              for directory in ("__PROJECT_CONFIG", "002_PROJECT_CONFIG")}
    for carrier in context["carriers"]:
        if carrier["id"] != atom_id:
            continue
        try:
            path = PurePosixPath(carrier["source_path"]).relative_to(control_path)
        except ValueError:
            continue
        plain_des_archive = archiving_spec and path.parent.name == "_DES" and path.name.startswith(f"{atom_id}-DES--")
        active_model = (not plain_des_archive and is_ontology_model_source(path)) or path.parent in custom
        scope = ontology_component_path(path)
        if ((carrier["status"] == "active" and active_model)
                or (job.arguments.get("targetStatus") == "active"
                    and (scope is not None or any(path.is_relative_to(root) for root in custom)))):
            return True
    return False


def needs_exact_archive(job, context):
    target = job.arguments.get("target")
    ref = target.get("ref_id") if isinstance(target, dict) else None
    if not isinstance(ref, str):
        return False
    will_archive = (job.name == "atom_lifecycle_archive" and not ref.endswith("-draft")
                    or job.name == "atom_lifecycle_change_status" and job.arguments.get("targetStatus") == "archived")
    if not will_archive and job.name != "atom_lifecycle_promote_draft":
        return False
    atom_id = ref.partition("@")[0]
    return any(row["read"] and row["id"] == atom_id and row["version"] <= context["max_archived_version"]
               for row in context["carriers"])
