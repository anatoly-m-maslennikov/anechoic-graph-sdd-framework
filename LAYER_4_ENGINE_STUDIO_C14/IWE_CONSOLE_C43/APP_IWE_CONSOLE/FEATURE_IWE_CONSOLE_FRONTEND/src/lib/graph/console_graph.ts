import type { QueryResult } from '../lib__shared';

type Query = (sql: string) => Promise<QueryResult>;
export type GraphNode = { id: string; label: string;
  kind: 'Atom' | 'Component' | 'Package' | 'Import'; depth: number };
export type GraphEdge = { source: string; target: string;
  type: string; violation?: boolean };
export type Graph = { nodes: GraphNode[]; edges: GraphEdge[] };
const quote = (value: string) => `'${value.replaceAll("'", "''")}'`;
const list = (values: string[]) => values.map(quote).join(', ');

async function rows(query: Query, sql: string): Promise<unknown[][]> {
  const all: unknown[][] = [];
  while (true) {
    const result = await query(`${sql} LIMIT 100 OFFSET ${all.length}`);
    all.push(...result.rows);
    if (all.length > 2000)
      throw new Error('Graph exceeds 2,000 rows. Narrow the query.');
    if (!result.has_more && result.rows.length < 100) return all;
    if (!result.rows.length)
      throw new Error('The graph query returned an incomplete page.');
  }
}

export async function relationTypes(query: Query): Promise<string[]> {
  const result = await rows(query,
    'SELECT DISTINCT relation_type FROM relations ORDER BY relation_type');
  return result.map(row => String(row[0]));
}

async function structureBindings(query: Query, refs: string[]) {
  const references = '    SELECT reference, exact_ref ' +
    `FROM native_references WHERE reference IN (${list(refs)})`;
  return rows(query, `WITH selected AS (
${references}
  ) SELECT DISTINCT p.node_key AS key, s.reference, 'Package' AS kind
    FROM implementation_rmedo b
    JOIN selected s ON (b.atom_id || '@' || b.version) = s.exact_ref
    JOIN import_nodes p ON p.relative_path = b.owner_path
      AND p.kind = 'package'
    UNION ALL SELECT c.component_id, s.reference, 'Component'
    FROM components c JOIN selected s ON c.manifest_ref = s.exact_ref
    ORDER BY kind DESC, key, reference`);
}

function relatedAtoms(query: Query, frontier: string[], types: string[]) {
  const members = list(frontier);
  return rows(query,
    'SELECT source_ref, target_ref, relation_type FROM relations ' +
    "WHERE source_kind = 'Atom' AND target_kind = 'Atom' " +
    `AND relation_type IN (${list(types)}) ` +
    `AND (source_ref IN (${members}) OR target_ref IN (${members})) ` +
    'ORDER BY source_ref, target_ref, relation_type');
}

function addBindings(
  nodes: Map<string, GraphNode>, edges: Map<string, GraphEdge>,
  bindings: unknown[][],
) {
  for (const [key, rawRef, rawKind] of bindings) {
    const kind = rawKind === 'Component' ? 'Component' : 'Package';
    const label = String(key);
    const id = kind === 'Component' ? `component:${label}` : label;
    const target = nodes.get(String(rawRef));
    if (!target) continue;
    nodes.set(id, { id, label, kind, depth: target.depth + 1 });
    edges.set(JSON.stringify([id, target.id, 'Spec Binding']), {
      source: id, target: target.id, type: 'Spec Binding',
    });
  }
}

export async function atomGraph(query: Query, refs: string[], depth: number,
  types: string[], includeStructure: boolean): Promise<Graph> {
  if (!Number.isSafeInteger(depth) || depth < 0)
    throw new Error('Depth must be a non-negative whole number.');
  if (refs.some(ref => !ref.trim()))
    throw new Error('Atom references must not be empty.');
  const exacts = refs.filter(ref => ref.includes('@'));
  const aliases = exacts.length ? await rows(query,
    'SELECT exact_ref, reference FROM native_references ' +
    `WHERE exact_ref IN (${list(exacts)}) ORDER BY exact_ref`) : [];
  const byExact = new Map(aliases.map(([exact, reference]) =>
    [String(exact), String(reference)]));
  const nodes = new Map<string, GraphNode>();
  for (const ref of refs) {
    const key = byExact.get(ref) ?? ref;
    if (!nodes.has(key)) nodes.set(key,
      { id: ref, label: ref, kind: 'Atom', depth: 0 });
  }
  const edges = new Map<string, GraphEdge>();
  let frontier = [...nodes.keys()];
  for (let hop = 0; hop <= depth && frontier.length && types.length; hop++) {
    const candidates = await relatedAtoms(query, frontier, types);
    const next: string[] = [];
    for (const [rawSource, rawTarget, rawType] of candidates) {
      const source = String(rawSource), target = String(rawTarget);
      const type = String(rawType);
      if (hop === depth && (!nodes.has(source) || !nodes.has(target)))
        continue;
      for (const id of [source, target]) if (!nodes.has(id)) {
        nodes.set(id, { id, label: id, kind: 'Atom', depth: hop + 1 });
        next.push(id);
      }
      edges.set(JSON.stringify([source, target, type]), {
        source: nodes.get(source)!.id, target: nodes.get(target)!.id, type,
      });
    }
    frontier = next;
  }
  if (includeStructure && nodes.size) {
    const bindings = await structureBindings(query, [...nodes.keys()]);
    addBindings(nodes, edges, bindings);
  }
  return { nodes: [...nodes.values()], edges: [...edges.values()] };
}

export async function importsGraph(
  query: Query, occurrences?: string[]): Promise<Graph> {
  if (occurrences && !occurrences.length) return { nodes: [], edges: [] };
  if (occurrences?.some(value => !value.trim()))
    throw new Error('Import occurrence keys must not be empty.');
  const where = occurrences ?
    ` WHERE e.occurrence_key IN (${list(occurrences)})` : '';
  const edgeRows = await rows(query,
    'SELECT DISTINCT e.source_key, e.target_key, ' +
    "CASE WHEN f.status IN ('denied', 'undeclared_bypass') " +
    'THEN true ELSE false END AS violation FROM import_edges e ' +
    'LEFT JOIN module_imports i ON i.occurrence_key = e.occurrence_key ' +
    'LEFT JOIN code_access_findings f ON f.source_key = i.source_key ' +
    'AND f.line = i.line AND f."column" = i."column" ' +
    `AND f.written_specifier = i.written_specifier${where} ` +
    'ORDER BY e.source_key, e.target_key, violation');
  const keys = [...new Set(edgeRows.flatMap(
    row => [String(row[0]), String(row[1])]))];
  if (!keys.length) return { nodes: [], edges: [] };
  const nodeRows = await rows(query,
    'SELECT node_key, kind, relative_path FROM import_nodes ' +
    `WHERE node_key IN (${list(keys)}) ORDER BY node_key`);
  const nodes = nodeRows.map(([key, kind, path]) => ({
    id: String(key), label: String(path || key),
    kind: kind === 'package' ? 'Package' as const :
      'Import' as const, depth: 0 }));
  const known = new Set(nodes.map(node => node.id));
  const edges = new Map<string, GraphEdge>();
  for (const [rawSource, rawTarget, violation] of edgeRows) {
    const source = String(rawSource), target = String(rawTarget);
    if (!known.has(source) || !known.has(target)) continue;
    const key = JSON.stringify([source, target]);
    edges.set(key, { source, target, type: 'Imports',
      violation: Boolean(violation) || edges.get(key)?.violation });
  }
  return { nodes, edges: [...edges.values()] };
}

export function graphLayout(graph: Graph, layout: 'vertical' | 'horizontal') {
  const levels = [...new Set(graph.nodes.map(node => node.depth))]
    .sort((a, b) => a - b);
  const positions = new Map<string, { x: number; y: number }>();
  let row = 0;
  for (const level of levels) {
    const nodes = graph.nodes.filter(node => node.depth === level);
    nodes.forEach((node, index) => {
      const x = 20 + (index % 5) * 220, y =
        20 + (row + Math.floor(index / 5)) * 110;
      positions.set(node.id, layout === 'vertical'
        ? { x, y } : { x: y * 2, y: x / 2 });
    });
    row += Math.ceil(nodes.length / 5);
  }
  const points = [...positions.values()];
  return { positions, width: Math.max(220, ...points.map(p =>
    p.x + 200)), height: Math.max(100, ...points.map(p => p.y + 80)) };
}

export function edgePoints(
  from: { x: number; y: number }, to: { x: number; y: number }) {
  const dx = to.x - from.x, dy = to.y - from.y;
  const scale = Math.max(Math.abs(dx) / 90, Math.abs(dy) / 25) || 1;
  const x = dx / scale, y = dy / scale;
  return { x1: from.x + 90 + x, y1: from.y + 25 + y,
    x2: to.x + 90 - x, y2: to.y + 25 - y };
}
