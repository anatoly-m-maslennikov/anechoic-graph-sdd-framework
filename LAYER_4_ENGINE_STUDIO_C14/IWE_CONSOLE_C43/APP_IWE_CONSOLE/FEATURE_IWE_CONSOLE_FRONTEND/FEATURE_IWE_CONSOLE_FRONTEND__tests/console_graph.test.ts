import assert from 'node:assert/strict';
import test from 'node:test';
import { loadLib } from './FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';
const { atomGraph, graphLayout, importsGraph } = await loadLib();
import type { QueryResult } from '../src/lib/lib__shared';

const result = (rows: unknown[][]) => ({
  rows, has_more: false } as QueryResult);
const relations = [['A', 'B', 'uses'], ['B', 'C',
  'uses'], ['C', 'A', 'other'], ['C', 'D', 'uses']];
async function query(sql: string): Promise<QueryResult> {
  if (sql.includes('FROM relations')) {
    const types = sql.match(/relation_type IN \(([^)]*)\)/)?.[1] ?? '';
    const frontier = sql.match(/source_ref IN \(([^)]*)\)/)?.[1] ?? '';
    return result(relations.filter(([a, b,
      type]) => types.includes(`'${type}'`) &&
      (frontier.includes(`'${a}'`) || frontier.includes(`'${b}'`))));
  }
  if (sql.includes('architecture_package_bindings')) {
    assert.match(sql, /b\.atom_ref = s\.exact_ref/);
    assert.match(sql, /c\.ref = s\.exact_ref/);
    return sql.includes("WHERE reference IN ('A'") ? result([['package:p',
      'A', 'Package'], ['C01', 'A', 'Component']]) : result([]);
  }
  if (sql.includes('FROM native_references')) return sql.includes(
    "'A@2'") ? result([['A@2', 'A']]) : result([['A@1', 'A@1']]);
  if (sql.includes('FROM import_nodes')) return result([[
    'module:a', 'module', 'a.py'], ['module:b', 'module', 'b.py']]);
  if (sql.includes('FROM import_edges')) {
    assert.match(sql, /module_imports/);
    assert.match(sql, /f\.written_specifier = i\.written_specifier/);
    return result([['module:a', 'module:b', true]]);
  }
  throw new Error(sql);
}

test('depth, filtering, cycles, bindings and layouts', async () => {
  const zero = await atomGraph(query, ['A', 'B'], 0, ['uses'], false);
  assert.deepEqual(zero.nodes.map(n => n.id), ['A', 'B']);
  assert.deepEqual(zero.edges.map(e => [e.source, e.target]), [['A', 'B']]);
  const one = await atomGraph(query, ['A'], 1, ['uses'], false);
  assert.deepEqual(one.nodes.map(n => n.id), ['A', 'B']);
  const two = await atomGraph(query, ['A'], 2, ['uses'], true);
  assert.deepEqual(two.nodes.map(n => n.id), [
    'A', 'B', 'C', 'package:p', 'component:C01']);
  assert.equal(two.edges.filter(e => e.type === 'Spec Binding').length, 2);
  assert.equal(two.edges.some(e => e.type === 'other'), false);
  assert.notDeepEqual(graphLayout(two, 'vertical').positions.get(
    'B'), graphLayout(two, 'horizontal').positions.get('B'));
  await assert.rejects(atomGraph(query, ['A'], -1, [], false), /Depth/);
});

test('escapes references and identifies violation edges', async () => {
  let seen = '';
  await atomGraph(async sql => { seen = sql; return result(
    []); }, ["A' OR 1=1--"], 0, ['uses'], false);
  assert.match(seen, /'A'' OR 1=1--'/);
  const graph = await importsGraph(query);
  assert.equal(graph.edges[0].violation, true);
});

test('uses the admitted relation and binding references without losing exact navigation',
  async () => {
  const current = await atomGraph(query, ['A@2'], 1, ['uses'], true);
  assert.deepEqual(current.nodes.map(n => n.id),
    ['A@2', 'B', 'package:p', 'component:C01']);
  assert.deepEqual(current.edges.map(({
    source, target }) => [source, target]), [
    ['A@2', 'B'], ['package:p', 'A@2'], ['component:C01', 'A@2'],
  ]);
  const archived = await atomGraph(query, ['A@1'], 1, ['uses'], true);
  assert.deepEqual(archived.nodes.map(n => n.id), ['A@1']);
  assert.deepEqual(archived.edges, []);
});
