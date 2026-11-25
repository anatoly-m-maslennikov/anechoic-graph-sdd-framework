
import assert from 'node:assert/strict';
import test from 'node:test';
import { loadLib } from './FEATURE_WORKBENCH_FRONTEND__tests__shared.mjs';
const { cleanAfterSave, newView, persistable, restore, storageKey, workspaceTabs, performAction } = await loadLib();

test('a new empty view starts clean', () => {
  const tab = newView(1);
  assert.equal(tab.sql, tab.savedSql);
  assert.equal(tab.dirty, false);
  assert.equal(tab.name, undefined);
});

test('single-statement save does not mark a multi-statement view clean', () => {
  const tab = { id: 'a', title: 'Worksheet 1', sql: 'SELECT 1; SELECT 2', cursor: 0, dirty: true };
  assert.equal(cleanAfterSave(tab, 'SELECT 1').dirty, true);
  assert.equal(cleanAfterSave({ ...tab, sql: 'SELECT 1' }, 'SELECT 1').dirty, false);
});

test('persisted workspaces keep scripts and sync state but never result rows', () => {
  const raw = persistable([{ id: 'a', title: 'One', name: 'Daily report', sql: 'SELECT 1', cursor: 8, dirty: true, syncDirty: false, result: { rows: [[1]] } }], 'a');
  assert.deepEqual(restore(raw), { tabs: [{ id: 'a', title: 'One', name: 'Daily report', sql: 'SELECT 1', cursor: 8, dirty: true, syncDirty: false, savedSql: undefined }], activeId: 'a' });
});

test('historical generated tab names become Views without losing the draft', () => {
  const result = restore(JSON.stringify({ activeId: 'old', tabs: [{ id: 'old', title: 'Worksheet 2', sql: 'SELECT 42', cursor: 3, dirty: true, name: 'My report' }] }));
  assert.equal(result.tabs[0].title, 'View 2');
  assert.equal(result.tabs[0].name, 'My report');
  assert.equal(result.tabs[0].sql, 'SELECT 42');
  assert.equal(result.activeId, 'old');
});

test('bound drafts use their own Project and Workspace key', () => {
  assert.equal(storageKey('anechoic'), 'anechoic.workbench.anechoic.workspace');
  assert.equal(storageKey('anechoic', 'chat-a', '/projects/a'), 'anechoic.workbench./projects/a.workspace.chat-a');
});

test('polling a result-free bound View does not dereference a missing local result', () => {
  const { tabs } = workspaceTabs({ active_view_id: 'a', views: [{ id: 'a', sql: '', cursor_position: 0, revision: 0 }] });
  assert.equal(tabs[0].id, 'a');
  assert.equal(tabs[0].result, undefined);
});

test('polling leaves an unsynced draft on its original revision', () => {
  const state = { active_view_id: 'a', views: [{ id: 'a', sql: 'SELECT remote', name: 'Remote', revision: 3 }] };
  const { tabs } = workspaceTabs(state, [{ id: 'a', title: 'View 1', sql: 'SELECT local', savedSql: 'SELECT old', dirty: true, syncDirty: true, revision: 2 }]);
  assert.equal(tabs[0].sql, 'SELECT local');
  assert.equal(tabs[0].revision, 2);
  assert.equal(tabs[0].serverSql, 'SELECT remote');
  assert.equal(tabs[0].serverRevision, 3);
});

test('polling a rebuilt View keeps its unsynced draft and follows the new result', () => {
  const result = { query_id: 'new', status: 'success' };
  const state = { active_view_id: 'a', views: [{ id: 'a', sql: 'SELECT remote', cursor_position: 0, revision: 3, result }] };
  const local = { id: 'a', sql: 'SELECT local', cursor: 7, savedSql: 'SELECT old', dirty: true, syncDirty: true, revision: 2, conflict: true, run: { query_id: 'old' }, result: { query_id: 'old', rows: [[1]] } };
  const tab = workspaceTabs(state, [local]).tabs[0];
  assert.equal(tab.sql, local.sql);
  assert.equal(tab.cursor, local.cursor);
  assert.equal(tab.revision, local.revision);
  assert.equal(tab.conflict, true);
  assert.equal(tab.serverRevision, 3);
  assert.equal(tab.run, result);
  assert.equal(tab.result, undefined);
  const fetched = { query_id: 'new', rows: [[2]] };
  assert.equal(workspaceTabs(state, [{ ...tab, result: fetched }]).tabs[0].result, fetched);
});

test('an acknowledged draft remains permanently unsaved after workspace polling', () => {
  const result = { query_id: 'retained', rows: [[42]] };
  const saved = { saved_query_id: 'previous' };
  const state = { active_view_id: 'a', views: [{ id: 'a', sql: 'SELECT draft', revision: 3, result }] };
  const local = { id: 'a', title: 'View 1', sql: 'SELECT draft', savedSql: 'SELECT saved', dirty: true, syncDirty: false, revision: 3, result, saved, saveError: 'Save refused' };
  const { tabs } = workspaceTabs(state, [local]);
  assert.equal(tabs[0].dirty, true);
  assert.equal(tabs[0].syncDirty, false);
  assert.equal(tabs[0].savedSql, 'SELECT saved');
  assert.equal(tabs[0].saveError, local.saveError);
  assert.equal(tabs[0].result, result);
  assert.equal(tabs[0].saved, saved);
});

test('a stale poll cannot overwrite an acknowledged permanent-unsaved draft', () => {
  const state = { active_view_id: 'a', views: [{ id: 'a', sql: 'SELECT before', cursor_position: 0, revision: 2 }] };
  const { tabs } = workspaceTabs(state, [{ id: 'a', title: 'View 1', sql: 'SELECT after', savedSql: 'SELECT saved', dirty: true, syncDirty: false, cursor: 4, revision: 3 }]);
  assert.equal(tabs[0].sql, 'SELECT after');
  assert.equal(tabs[0].revision, 3);
  assert.equal(tabs[0].dirty, true);
});


test('completed runs reject missing or mismatched result IDs and keep save outcomes', async () => {
  for (const [kind, queryId, fetchedId, expectedError] of [
    ['run', null, null, 'The completed query has no result ID.'],
    ['run', 'run-1', 'run-2', 'The View result changed before it could be displayed.'],
    ['save', null, null, 'The completed query has no result ID.'],
    ['save', 'run-1', 'run-2', 'The View result changed before it could be displayed.'],
  ]) {
    let tab = { id: 'a', sql: 'SELECT 1' };
    let fetches = 0;
    let refreshed = false;
    const ctx = {
      active: tab, workspaceReady: true, savedBusy: false,
      boundApi: {
        run: async () => ({ status: 'success', revision: 1, query_id: queryId, save_error: 'Save refused' }),
        fetch: async () => { fetches++; return { query_id: fetchedId, rows: [['wrong result']] }; },
      },
      updateTab: (_id, changes) => { tab = { ...tab, ...changes }; },
      fail: (_id, error) => { throw error; }, syncBeforeRun: async () => true, tabById: () => tab,
      message: String, acceptResult: () => assert.fail('Unexpected result'), acceptSaved: () => assert.fail('Unexpected save'),
      refreshSaved: async () => { refreshed = true; }, reportLogWarning: () => {}, resetGrid: () => {},
      resultDisplay: () => ({ rowSizing: 'fixed', fixedPageSize: 25 }), grid: () => ({}),
    };
    await performAction(ctx, kind, 0);
    assert.equal(tab.error, expectedError);
    assert.equal(tab.busy, false);
    assert.equal(tab.result, undefined);
    assert.equal(tab.saveError, 'Save refused');
    assert.equal(refreshed, kind === 'save');
    assert.equal(fetches, queryId ? 1 : 0);
  }
});
