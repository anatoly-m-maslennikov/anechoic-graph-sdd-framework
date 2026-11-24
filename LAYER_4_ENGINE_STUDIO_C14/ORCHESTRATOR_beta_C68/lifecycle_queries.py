"""Select generation-pinned lifecycle context from the private database."""
from contextlib import closing
import json
import re

from .jobs import UnixConnection


_SQL = '''WITH RECURSIVE
    native AS (
      SELECT a.reference AS ref, n.exact_ref AS exact_ref,
        split_part(n.exact_ref, '@', 1) AS id,
        CASE WHEN a.relative_path = '.' THEN a.filename ELSE a.relative_path || '/' || a.filename END AS path,
        a."header.state.version" AS version, a."header.state.status" AS status, a.status_group,
        r.target_kind AS owner_kind, r.target_ref AS owner_ref
      FROM main.atoms a JOIN main.native_references n USING (reference)
      LEFT JOIN main.relations r ON r.source_kind='Atom' AND r.source_ref=a.reference
        AND r.relation_type='CONTAINED_BY' AND NOT r.derived
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
        OR n.ref IN (SELECT source_ref FROM main.relations WHERE relation_type='CONTAINED_BY'
            AND NOT derived AND target_kind='Atom' AND target_ref={target_lit})
        OR n.ref IN (SELECT source_ref FROM main.relations WHERE relation_type='IS_REPLACEMENT_FOR'
            AND NOT derived AND target_ref={target_lit}) AND n.status_group='Current'
    ),
    numbers AS (
      SELECT regexp_extract(reference, '^{prefix}-([TS])-([0-9]+)(@|$)', 1) AS family,
        ltrim(regexp_extract(reference, '^{prefix}-([TS])-([0-9]+)(@|$)', 2), '0') AS number
      FROM main.atoms WHERE {numbers} AND starts_with(reference, '{prefix}-')
    ),
    SELECT g.id, g.structure, {model_sql}, json_extract(g.model, '$.ticket_labels')::VARCHAR,
      coalesce((SELECT arg_max(number, (length(number), number)) FROM numbers WHERE family='T' AND number<>''), '0'),
      coalesce((SELECT arg_max(number, (length(number), number)) FROM numbers WHERE family='S' AND number<>''), '0'),
      coalesce((SELECT to_json(list(struct_pack(ref := ref, _exact_ref := exact_ref, source_path := path,
        _source_sha256 := CASE WHEN should_read THEN json_extract_string((SELECT hashes FROM main.generation_carriers), '/' || replace(replace(path, '~', '~0'), '/', '~1')) ELSE NULL END, version := version, status := status, status_group := status_group,
        id := id, owner_kind := owner_kind, owner_ref := owner_ref, read := should_read)))::VARCHAR
        FROM selected), '[]'),
      EXISTS(SELECT 1 FROM main.relations WHERE relation_type='CONTAINED_BY' AND NOT derived
        AND target_kind='Atom' AND target_ref={target_lit}) OR EXISTS(SELECT 1 FROM native parent JOIN native child
        ON starts_with(child.path, regexp_replace(parent.path, '[.]md$', '') || '/')
        WHERE parent.id={target_lit} AND (parent.ref={exact_lit} OR parent.status_group='Current')), 
      coalesce((SELECT to_json(list(DISTINCT lens))::VARCHAR FROM main.lifecycle_lenses WHERE lens IS NOT NULL), '[]')
    FROM main.generation g'''

def _literal(value):
    return "'" + value.replace("'", "''") + "'"


def lifecycle_sql(prefix, name, arguments):
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
    needs_model = (is_create and isinstance(template, str) and template in {'project_contract', 'axiom', 'applicable_principle'}
                   or '-S-' in target_id and name in {'atom_lifecycle_promote_draft', 'atom_lifecycle_change_status'})
    model_sql = 'g.model' if needs_model else 'NULL'
    return _SQL.format(prefix=prefix, target_lit=target_lit, exact_lit=exact_lit, owner_lit=owner_lit,
                       sources=sources, numbers=numbers, model_sql=model_sql)


def lifecycle_context(socket_path, instance_id, base, prefix, name, arguments):
    sql = lifecycle_sql(prefix, name, arguments)
    request = json.dumps({'instance_id': instance_id, 'sql': sql})
    with closing(UnixConnection(socket_path)) as connection:
        connection.request('POST', '/database', request, {'Content-Type': 'application/json'})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError('Kernel refused lifecycle context query')
        rows = json.loads(response.read())['result']['rows']
    if not isinstance(rows, list) or len(rows) != 1 or len(rows[0]) != 9 or rows[0][0] != base:
        raise ValueError('Kernel generation changed before lifecycle context query')
    _, structure, model, labels, ticket, spec, carriers, descendants, lenses = rows[0]
    model = json.loads(model) if model is not None else None
    structure, labels, carriers, lenses = map(json.loads, (structure, labels, carriers, lenses))
    if (not isinstance(structure, dict) or model is not None and not isinstance(model, dict) or not isinstance(labels, list)
            or not all(isinstance(x, str) for x in labels) or not isinstance(carriers, list)
            or not isinstance(lenses, list) or not all(isinstance(x, str) for x in lenses)
            or type(descendants) is not bool
            or any(not isinstance(x, str) or not re.fullmatch(r'0|[1-9][0-9]*', x) for x in (ticket, spec))):
        raise ValueError('Kernel returned invalid lifecycle context')
    return {'structure': structure, 'model': model, 'ticket_labels': labels, 'max_numbers': {'T': ticket, 'S': spec},
            'carriers': carriers, 'has_descendants': descendants, 'lenses': lenses}
