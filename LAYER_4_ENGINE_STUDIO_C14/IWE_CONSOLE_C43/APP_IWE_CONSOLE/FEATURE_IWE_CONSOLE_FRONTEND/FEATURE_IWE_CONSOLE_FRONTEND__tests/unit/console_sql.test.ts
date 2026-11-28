import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadLib } from '../FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';
const { consoleView, editConsoleSql } = await loadLib();

test('View directives ignore strings, comments and nested SQL', () => {
  assert.deepEqual(consoleView('SELECT 1'),
    { kind: 'table', layout: 'vertical' });
  assert.deepEqual(consoleView('SELECT 1 VIEW GRAPH HORIZONTAL'),
    { kind: 'graph', layout: 'horizontal' });
  assert.equal(consoleView('SELECT 1 VIEW DOC').kind, 'document');
  assert.deepEqual(consoleView('SELECT 1 VIEW IMPORTS'),
    { kind: 'imports', layout: 'vertical' });
  assert.deepEqual(consoleView('SELECT 1 VIEW IMPORTS VERTICAL'),
    { kind: 'imports', layout: 'vertical' });
  assert.deepEqual(consoleView(
    'SELECT 1 VIEW IMPORTS /* layout */ HORIZONTAL'),
    { kind: 'imports', layout: 'horizontal' });
  assert.equal(consoleView('SELECT 1 VIEW STRUCTURE').kind, 'structure');
  assert.equal(consoleView("SELECT 'VIEW GRAPH'").kind, 'table');
  assert.equal(consoleView('SELECT 1 -- VIEW GRAPH').kind, 'table');
  assert.equal(consoleView('SELECT (SELECT 1 VIEW GRAPH)').kind, 'table');
});

test('recognizes View directives among SQL comments and keeps SQL expressions distinct', () => {
  const cases = [
    ['SELECT 1 VIEW /* note */ GRAPH -- orientation', 'graph'],
    ["SELECT 1 /* outer /* nested */ ' */ VIEW GRAPH", 'graph'],
    ["SELECT $value$'() VIEW TABLE$value$ AS label VIEW DOC", 'document'],
    [String.raw`SELECT E'keep\' quote' AS label VIEW DOC`, 'document'],
    ['SELECT $$VIEW GRAPH$$', 'table'],
    ['SELECT 1 VIEW "name" GRAPH', 'table'],
    ['SELECT 1 VIEW GRAPH (1)', 'table'],
    ['SELECT 1 VIEW GRAPH /*/', 'table'],
    ['SELECT 1 AS name$VIEW GRAPH', 'table'],
  ] as const;
  for (const [sql, kind] of cases) assert.equal(
    consoleView(sql).kind, kind, sql);
});

test('builder edits only outer LIMIT and preserves directives', () => {
  assert.equal(editConsoleSql('SELECT (SELECT 1 LIMIT 1) LIMIT 5 VIEW GRAPH',
    'limit', '10'), 'SELECT (SELECT 1 LIMIT 1) LIMIT 10 VIEW GRAPH');
  assert.equal(editConsoleSql(
    "SELECT * FROM atoms WHERE x = 1 OR y = 2 ORDER BY x",
      'template', "O'Reilly"),
    `SELECT * FROM atoms WHERE (x = 1 OR y = 2) AND "header.context.template" = 'O''Reilly' ORDER BY x`);
  const first = editConsoleSql('SELECT * FROM atoms', 'component', 'C1');
  assert.equal(editConsoleSql(first, "component", "C2"),
    `SELECT * FROM atoms WHERE "header.container.component" = 'C2'`);

  assert.equal(editConsoleSql("SELECT '--' FROM atoms LIMIT 1",
    'limit', '2'), "SELECT '--' FROM atoms LIMIT 2");
  assert.throws(() => editConsoleSql(
    'SELECT 1 -- LIMIT 1', 'limit', '2'), /comments/);
  assert.throws(() => editConsoleSql(
    'SELECT 1 LIMIT 1 OFFSET 2', 'limit', '3'), /safely/);
  assert.throws(() => editConsoleSql(
    'SELECT * FROM a UNION SELECT * FROM b', 'tier', '1'), /complex/);
});

test('changes and removes earlier builder controls after adding another filter', () => {
  const source = 'SELECT reference, "header.tier" FROM atoms VIEW DOCUMENT';
  const byTier = editConsoleSql(source, 'tier', '-1');
  assert.match(byTier, /WHERE "header.tier" = -1/);
  const byBoth = editConsoleSql(byTier, 'component', 'C46');
  const byAnotherTier = editConsoleSql(byBoth, 'tier', '1');
  assert.match(byAnotherTier,
    /WHERE "header.tier" = 1 AND "header.container.component" = 'C46'/);
  assert.equal(editConsoleSql(byAnotherTier, 'tier', ''),
    `SELECT reference, "header.tier" FROM atoms WHERE "header.container.component" = 'C46' VIEW DOCUMENT`);
});
