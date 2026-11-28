import type { QueryResult } from '../../lib__shared';

export const STRUCTURE_SQL =
  `SELECT c.component_id AS id, c.parent_component_id AS parent,
  'Component' AS kind, c.name, c.purpose, c.manifest_ref AS manifest,
  (SELECT string_agg(n.exact_ref, '|' ORDER BY n.exact_ref)
   FROM atoms a JOIN native_references n USING (reference)
   WHERE a.status_group = 'Current' AND a."header.state.status" = 'active'
     AND split_part(a.reference, '-', 2) = 'S'
     AND lower(a."header.context.template") = 'solution'
     AND coalesce(json_extract_string(to_json(a), '$."header.tier"'),
         json_extract_string(to_json(a), '$."header.structure.tier"'),
         json_extract_string(to_json(a), '$."header.context.tier"')) = '0'
     AND EXISTS (SELECT 1 FROM relations r WHERE r.source_kind = 'Atom'
       AND r.source_ref = a.reference AND r.target_kind = 'Component'
       AND r.target_ref = c.component_id AND NOT r.derived
       AND r.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY'))
     AND EXISTS (SELECT 1 FROM relations r WHERE r.source_kind = 'Atom'
       AND r.source_ref = a.reference AND r.target_kind = 'Atom'
       AND r.target_ref = c.manifest_ref AND r.relation_type = 'ANSWERS'
       AND NOT r.derived)) AS solutions
FROM components c
UNION ALL
SELECT seed_id, parent_component_id, 'Component Seed', seed_id, purpose,
  manifest_ref, CASE WHEN has_solution THEN manifest_ref END
FROM component_seeds`;

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
