import type { QueryResult } from './types';

export const STRUCTURE_SQL =
  `SELECT component_id AS id, parent, 'Component' AS kind,
  COALESCE(json_extract_string(fields, '$.name'), component_id) AS name,
  json_extract_string(component_extra, '$.purpose') AS purpose,
  s.ref AS manifest,
  (SELECT string_agg(n.exact_ref, '|' ORDER BY n.exact_ref) FROM mrt_atoms a
   JOIN native_references n ON n.reference = a.reference
   WHERE a."header.container.component" = s.component_id
     AND a."header.context.template" = 'solution' AND a."header.tier" = 0
     AND a."header.state.status" = 'active' AND a.status_group = 'Current'
     AND EXISTS (SELECT 1 FROM relations r WHERE r.source_kind = 'Atom'
       AND r.source_ref = a.reference ` +
    `AND r.target_kind = 'Atom' AND r.target_ref = s.ref
       AND r.relation_type = 'ANSWERS' AND NOT r.derived)) AS solutions
FROM mrt_project_structure s
UNION ALL
SELECT seed_id, parent, 'Component Seed', seed_id,
  json_extract_string(fields, '$.purpose'), ref,
  CASE WHEN json_extract_string(fields, '$.solution') IS NOT NULL THEN ` +
    `ref ELSE NULL END
FROM mrt_component_seeds`;

export type StructureEntry = {
  id: string; parent: string; kind: string; name: string; purpose: string;
  manifest: string; solutions: string[]; depth: number;
};

export function structureEntries(result: QueryResult): StructureEntry[] {
  const indexes = ['id', 'parent', 'kind',
    'name', 'purpose', 'manifest', 'solutions']
    .map(name => result.columns.findIndex(column => column.name === name));
  if (indexes.some(index => index < 0)) return [];
  const entries = result.rows.map(row => {
    const [id, parent, kind, name, purpose, manifest,
      solutions] = indexes.map(i => String(row[i] ?? ''));
    return { id, parent, kind, name, purpose, manifest, solutions:
      solutions ? solutions.split('|') : [], depth: 0 };
  }).sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  const output: StructureEntry[] = [];
  const seen = new Set<StructureEntry>();
  function append(entry: StructureEntry, depth: number) {
    if (seen.has(entry)) return;
    seen.add(entry);
    output.push({ ...entry, depth });
    for (const child of entries) if (
      child.parent === entry.id) append(child, depth + 1);
  }
  for (const entry of entries) if (!entries.some(parent =>
    parent.id === entry.parent)) append(entry, 0);
  for (const entry of entries) append(entry, 0);
  return output;
}
