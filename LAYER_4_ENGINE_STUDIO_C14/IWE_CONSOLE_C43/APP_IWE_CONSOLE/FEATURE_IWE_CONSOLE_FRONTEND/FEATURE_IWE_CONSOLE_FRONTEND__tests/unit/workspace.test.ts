
import assert from 'node:assert/strict';
import test from 'node:test';
import type { QueryResult, SavedIdentity,
  ViewResult } from '../../src/lib/lib__shared';
import { loadLib } from '../FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';
const {
  cleanAfterSave, newView, persistable, readConsoleStorage,
  restore, storageKey, workspaceTabs,
} = await loadLib();

function queryResult(queryId: string, rows: unknown[][]): QueryResult {
  return {
    sql: 'SELECT 1', query_id: queryId, columns:
      [{ name: 'value', type: 'INTEGER' }], rows,
    row_count: rows.length, column_count: 1,
      offset: 0, page_size: 100, has_more: false,
  };
}

test('a new empty view starts clean', () => {
  const tab: Parameters<typeof persistable>[0][number] = newView(1);
  assert.equal(tab.sql, tab.savedSql);
  assert.equal(tab.dirty, false);
  assert.equal(tab.name, undefined);
});

test('single-statement save does not mark a multi-statement view clean', () => {
  const tab = { id: 'a', title: 'Worksheet 1', sql:
    'SELECT 1; SELECT 2', cursor: 0, dirty: true };
  assert.equal(cleanAfterSave(tab, 'SELECT 1').dirty, true);
  assert.equal(cleanAfterSave({ ...tab, sql:
    'SELECT 1' }, 'SELECT 1').dirty, false);
});

test('persisted workspaces keep scripts and sync state but never result rows', () => {
  const raw = persistable([{
    id: 'a', title: 'One', name: 'Daily report', sql: 'SELECT 1', cursor: 8,
    dirty: true, syncDirty: false, result: queryResult('result', [[1]]),
  }], 'a');
  assert.deepEqual(restore(raw), { tabs: [{ id:
    'a', title: 'One', name: 'Daily report', sql:
    'SELECT 1', cursor: 8, dirty: true, syncDirty:
      false, savedSql: undefined }], activeId: 'a' });
});

test('historical generated tab names become Views without losing the draft', () => {
  const result = restore(JSON.stringify({
    activeId: 'old', tabs: [{ id: 'old', title:
    'Worksheet 2', sql: 'SELECT 42', cursor:
      3, dirty: true, name: 'My report' }] }));
  assert.ok(result);
  assert.equal(result.tabs[0].title, 'View 2');
  assert.equal(result.tabs[0].name, 'My report');
  assert.equal(result.tabs[0].sql, 'SELECT 42');
  assert.equal(result.activeId, 'old');
});

test('bound drafts use their own Project and Workspace key', () => {
  assert.equal(storageKey('anechoic'),
    'anechoic.iwe_console.anechoic.workspace');
  assert.equal(
    storageKey('anechoic', 'chat-a', '/projects/a'),
    'anechoic.iwe_console./projects/a.workspace.chat-a',
  );
});

test('copies Workbench preferences while giving IWE Console values precedence', () => {
  const key = `${storageKey('anechoic', 'chat-a')}:preferences`;
  const oldKey = 'anechoic.workbench.anechoic.workspace.chat-a:preferences';
  const entries = new Map([[oldKey, '{"theme":"dark"}']]);
  const storage = {
    getItem: (name: string) => entries.get(name) ?? null,
    setItem: (name: string, value: string) => entries.set(name, value),
  };
  assert.equal(readConsoleStorage(storage, key, false), null);
  assert.equal(readConsoleStorage(storage, key), '{"theme":"dark"}');
  assert.equal(entries.get(key), '{"theme":"dark"}');
  entries.set(key, '{"theme":"light"}');
  assert.equal(readConsoleStorage(storage, key), '{"theme":"light"}');
  assert.equal(entries.get(oldKey), '{"theme":"dark"}');
  entries.delete(key);
  const fullStorage = {
    ...storage,
    setItem() { throw new DOMException(
      'Storage is full', 'QuotaExceededError'); },
  };
  assert.equal(readConsoleStorage(fullStorage, key), '{"theme":"dark"}');
});

test('polling a result-free bound View does not dereference a missing local result', () => {
  const { tabs } = workspaceTabs({ active_view_id: 'a', views:
    [{ id: 'a', sql: '', cursor_position: 0, revision: 0 }] });
  assert.equal(tabs[0].id, 'a');
  assert.equal(tabs[0].result, undefined);
});

test('polling leaves an unsynced draft on its original revision', () => {
  const state = { active_view_id: 'a', views: [
    { id: 'a', sql: 'SELECT remote', name:
      'Remote', cursor_position: 0, revision: 3 },
  ] };
  const { tabs } = workspaceTabs(state, [{
    id: 'a', title: 'View 1', sql: 'SELECT local', cursor: 0,
    savedSql: 'SELECT old', dirty: true, syncDirty: true, revision: 2,
  }]);
  const [tab] = tabs;
  assert.equal(tab.sql, 'SELECT local');
  assert.equal(tab.revision, 2);
  assert.ok('serverRevision' in tab);
  assert.equal(tab.serverSql, 'SELECT remote');
  assert.equal(tab.serverRevision, 3);
});

test('polling a rebuilt View keeps its unsynced draft and follows the new result', () => {
  const result = { query_id: 'new', status: 'success' } satisfies ViewResult;
  const state = { active_view_id: 'a', views: [{ id: 'a', sql:
    'SELECT remote', cursor_position: 0, revision: 3, result }] };
  const local = {
    id: 'a', title: 'View 1', sql: 'SELECT local',
      cursor: 7, savedSql: 'SELECT old',
    dirty: true, syncDirty: true, revision: 2, conflict: true,
    run: { query_id: 'old', status: 'success' } satisfies ViewResult,
      result: queryResult('old', [[1]]),
  };
  const tab = workspaceTabs(state, [local]).tabs[0];
  assert.equal(tab.sql, local.sql);
  assert.equal(tab.cursor, local.cursor);
  assert.equal(tab.revision, local.revision);
  assert.ok('serverRevision' in tab);
  assert.equal(tab.conflict, true);
  assert.equal(tab.serverRevision, 3);
  assert.equal(tab.run, result);
  assert.equal(tab.result, undefined);
  const fetched = queryResult('new', [[2]]);
  assert.equal(workspaceTabs(state, [{ ...tab,
    result: fetched }]).tabs[0].result, fetched);
});

test('an acknowledged draft remains permanently unsaved after workspace polling', () => {
  const result = { ...queryResult('retained', [[42]]),
    status: 'success' } satisfies QueryResult & ViewResult;
  const saved: SavedIdentity = { saved_query_id: 'previous',
    saved_query_url: '/saved/previous', sql: 'SELECT saved', kind: 'query' };
  const state = { active_view_id: 'a', views: [{ id: 'a', sql:
    'SELECT draft', cursor_position: 0, revision: 3, result }] };
  const local = {
    id: 'a', title: 'View 1', sql: 'SELECT draft',
      cursor: 0, savedSql: 'SELECT saved', dirty: true,
    syncDirty: false, revision: 3, result, saved, saveError: 'Save refused',
  };
  const { tabs } = workspaceTabs(state, [local]);
  assert.equal(tabs[0].dirty, true);
  assert.equal(tabs[0].syncDirty, false);
  assert.equal(tabs[0].savedSql, 'SELECT saved');
  assert.equal(tabs[0].saveError, local.saveError);
  assert.equal(tabs[0].result, result);
  assert.equal(tabs[0].saved, saved);
});

test('a stale poll cannot overwrite an acknowledged permanent-unsaved draft', () => {
  const state = { active_view_id: 'a', views: [{ id: 'a', sql:
    'SELECT before', cursor_position: 0, revision: 2 }] };
  const { tabs } = workspaceTabs(state, [{ id:
    'a', title: 'View 1', sql: 'SELECT after',
    savedSql: 'SELECT saved', dirty: true,
      syncDirty: false, cursor: 4, revision: 3 }]);
  assert.equal(tabs[0].sql, 'SELECT after');
  assert.equal(tabs[0].revision, 3);
  assert.equal(tabs[0].dirty, true);
});

