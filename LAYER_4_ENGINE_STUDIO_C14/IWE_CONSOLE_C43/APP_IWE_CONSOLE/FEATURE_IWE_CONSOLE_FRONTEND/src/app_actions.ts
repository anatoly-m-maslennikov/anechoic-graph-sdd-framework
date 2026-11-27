import type { WorkspaceApi, CheckResult, Command, GridState, QueryResult, ResultDisplayPreferences, SavedIdentity, ViewResult } from './lib/lib__shared';
import { consoleView, newView } from './lib/lib__shared';

type Check = { sql: string; result: CheckResult } | { sql: string; error: string };
export type Tab = Omit<ReturnType<typeof newView>, 'id'> & { id: string; name?: string; busy?: boolean; error?: string; saveError?: string; result?: QueryResult; check?: Check; saved?: SavedIdentity; revision?: number; run?: ViewResult; conflict?: boolean; syncDirty?: boolean; serverSql?: string; serverRevision?: number };
type ActionContext = {
  active: Tab | undefined; workspaceReady: boolean; savedBusy: boolean; boundApi: WorkspaceApi | undefined;
  updateTab: (id: string, changes: Partial<Tab>) => void; fail: (id: string, error: unknown, conflict?: boolean) => void;
  syncBeforeRun: (id: string) => Promise<boolean>; tabById: (id: string) => Tab | undefined;
  message: (error: unknown) => string; acceptResult: (id: string, result: QueryResult) => void;
  acceptSaved: (id: string, saved: SavedIdentity) => void; refreshSaved: () => Promise<void>;
  reportLogWarning: (id: string, warning?: string) => void; resetGrid: () => void;
  resultDisplay: () => ResultDisplayPreferences; grid: () => GridState;
};

export async function performAction(ctx: ActionContext, kind: 'run' | 'check' | 'save', cursor: number, name?: string) {
  const { active, workspaceReady, savedBusy, updateTab, boundApi, fail, syncBeforeRun, tabById, message, acceptResult, acceptSaved, refreshSaved, reportLogWarning } = ctx;
  const tab = active; if (!workspaceReady || !tab || tab.busy || savedBusy) return;
  updateTab(tab.id, { busy: true, error: '', saveError: undefined, ...(kind === 'check' ? { check: undefined } : {}) });
  if (!boundApi) { fail(tab.id, new Error('Workspace is unavailable.')); return; }
  if (!await syncBeforeRun(tab.id)) { updateTab(tab.id, { busy: false }); return; }
  const current = tabById(tab.id); if (!current) return;
  if (current.syncDirty || current.conflict) {
    fail(tab.id, new Error('The View changed before its SQL could be submitted.'));
    return;
  }
  if (kind === 'check') {
    try {
      const result = await boundApi.check(current.id, cursor);
      updateTab(current.id, { busy: false, check: { sql: current.sql, result } });
    } catch (error) {
      if (error instanceof TypeError) fail(current.id, error);
      else updateTab(current.id, { busy: false, check: { sql: current.sql, error: message(error) } });
    }
    return;
  }
  try {
    const response = await boundApi.run(current.id, cursor, kind === 'save' ? { save: true, ...(name ? { name } : {}) } : {});
    if (response.revision !== current.revision) {
      updateTab(current.id, { run: undefined, result: undefined });
      throw new Error('The View changed before its query could be displayed.');
    }
    ctx.resetGrid(); updateTab(current.id, { revision: response.revision, run: response, result: undefined, saveError: response.save_error });
    if (response.status === 'failed') updateTab(current.id, { busy: false, error: response.error || 'Query failed' });
    else if (response.query_id) {
      const result = await fetchViewResult(boundApi, current.id, current.sql, response.query_id, ctx.resultDisplay(), ctx.grid());
      if (result) acceptResult(current.id, result);
      else updateTab(current.id, { busy: false, error: 'The View result changed before it could be displayed.' });
    } else updateTab(current.id, { busy: false, error: 'The completed query has no result ID.' });
    if (kind === 'save') {
      if (!response.save_error && response.saved_query_id && response.saved_query_url) acceptSaved(current.id, { saved_query_id: response.saved_query_id, saved_query_url: response.saved_query_url, kind: 'query', sql: current.sql, ...(name ? { name } : {}) });
      await refreshSaved();
    }
    reportLogWarning(current.id, response.query_log_error);
  } catch (error) { fail(current.id, error); }
}


type SyncContext = {
  syncing: Map<string, Promise<boolean>>; tabById: (id: string) => Tab | undefined;
  boundApi: WorkspaceApi | undefined; fail: (id: string, error: unknown, conflict?: boolean) => void;
  updateTab: (id: string, changes: Partial<Tab>) => void;
};

export function synchronizeDraft(ctx: SyncContext, id: string): Promise<boolean> {
  const { syncing, tabById, boundApi, fail, updateTab } = ctx;
  const pending = syncing.get(id); if (pending) return pending;
  const tab = tabById(id);
  if (!boundApi || !tab?.syncDirty || tab.conflict) return Promise.resolve(!tab?.conflict);
  if (!Number.isInteger(tab.revision)) { fail(id, new Error('View revision is unavailable'), true); return Promise.resolve(false); }
  const submitted = { sql: tab.sql, cursor: tab.cursor, revision: tab.revision };
  let request!: Promise<boolean>;
  request = (async () => {
    try {
      const server = await boundApi!.update(id, submitted.sql, submitted.revision!, submitted.cursor);
      if (server.id !== id || server.sql !== submitted.sql) throw new Error('The View update receipt did not match the submitted SQL.');
      const latest = tabById(id);
      if (latest && (latest.sql !== submitted.sql || latest.cursor !== submitted.cursor)) {
        updateTab(id, { revision: server.revision, run: server.result, check: undefined, syncDirty: true, conflict: false, serverSql: undefined, serverRevision: undefined });
      } else updateTab(id, { revision: server.revision, run: server.result, syncDirty: false, conflict: false, serverSql: undefined, serverRevision: undefined });
      return true;
    } catch (error) { fail(id, error, true); return false; }
    finally { if (syncing.get(id) === request) syncing.delete(id); }
  })();
  syncing.set(id, request);
  return request;
}

function gridColumn(active: Tab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(`Result column index (0-${result.columns.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) && index >= 0 && index < result.columns.length ? index : -1;
}
function gridRow(active: Tab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(`Result row index on this page (0-${result.rows.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) && index >= 0 && index < result.rows.length ? index : -1;
}

function resultValue(value: unknown) {
  if (value === null) return 'NULL';
  try { return typeof value === 'object' ? JSON.stringify(value) : String(value); }
  catch { return String(value); }
}

function copyResult(value: unknown) {
  void navigator.clipboard?.writeText(resultValue(value)).catch(() => {});
}

function filterGrid(active: Tab | undefined, grid: GridState, setGrid: (next: GridState) => void) {
  if (!active?.result || active.busy) return;
  const column = gridColumn(active);
  if (column < 0) return;
  const value = window.prompt(`Filter ${active.result.columns[column].name}`, grid.filters.find((item) => item.column === column)?.value ?? '');
  if (value === null) return;
  const filters = grid.filters.filter((item) => item.column !== column);
  if (value) filters.push({ column, operator: 'contains', value });
  setGrid({ ...grid, filters });
}

export function gridCommands(getActive: () => Tab | undefined, getGrid: () => GridState, setGrid: (next: GridState) => void): Command[] {
  const active = getActive();
  const result = active?.result;
  const grid = getGrid();
  const enabled = !!result && !active?.busy;
  const sort = (direction: 'asc' | 'desc') => {
    const column = gridColumn(getActive());
    if (column < 0) return;
    const current = getGrid();
    setGrid({ ...current, sort: [...current.sort.filter((item) => item.column !== column), { column, direction }] });
  };
  const group = (direction: 'asc' | 'desc') => {
    const column = gridColumn(getActive());
    if (column >= 0) setGrid({ ...getGrid(), group_by: { column, direction } });
  };
  return [
    { id: 'grid-copy-value', label: 'Result grid: Copy cell value', enabled: !!result, run: () => {
      const row = gridRow(getActive());
      const column = gridColumn(getActive());
      if (row >= 0 && column >= 0) copyResult(result!.rows[row][column]);
    } },
    { id: 'grid-show-value', label: 'Result grid: Show full cell value', enabled: !!result, run: () => {
      const row = gridRow(getActive());
      const column = gridColumn(getActive());
      if (row >= 0 && column >= 0) window.alert(resultValue(result!.rows[row][column]));
    } },
    { id: 'grid-copy-row', label: 'Result grid: Copy row', enabled: !!result, run: () => {
      const row = gridRow(getActive());
      if (row >= 0) copyResult(result!.rows[row]);
    } },
    { id: 'grid-sort-asc', label: 'Result grid: Sort column ascending', enabled, run: () => sort('asc') },
    { id: 'grid-sort-desc', label: 'Result grid: Sort column descending', enabled, run: () => sort('desc') },
    { id: 'grid-group-asc', label: 'Result grid: Group column ascending', enabled, run: () => group('asc') },
    { id: 'grid-group-desc', label: 'Result grid: Group column descending', enabled, run: () => group('desc') },
    { id: 'grid-clear-group', label: 'Result grid: Clear grouping', enabled: enabled && !!grid.group_by, run: () => setGrid({ ...getGrid(), group_by: undefined }) },
    { id: 'grid-filter', label: 'Result grid: Filter column', enabled, run: () => filterGrid(getActive(), getGrid(), setGrid) },
    { id: 'grid-clear-filter', label: 'Result grid: Clear filter', enabled: enabled && grid.filters.length > 0, run: () => setGrid({ ...getGrid(), filters: [] }) },
  ];
}

export function resultPager(ctx: {
  workspace: () => WorkspaceApi | undefined; active: () => Tab | undefined;
  tabById: (id: string) => Tab | undefined; updateTab: (id: string, changes: Partial<Tab>) => void;
  message: (error: unknown) => string;
}) {
  const paging = new Map<string, number>();
  let pageRequest = 0;
  return async (offset: number, pageSize: number | undefined, grid: GridState) => {
    const tab = ctx.active(), workspace = ctx.workspace();
    if (!tab?.result || tab.busy || consoleView(tab.result.sql).kind !== 'table') return;
    const { query_id: queryId, sql } = tab.result;
    const request = ++pageRequest;
    paging.set(tab.id, request);
    const current = () => {
      const latest = ctx.tabById(tab.id);
      return paging.get(tab.id) === request && !latest?.busy && latest?.result?.query_id === queryId;
    };
    try {
      if (!workspace || !pageSize) throw new Error('Workspace is unavailable.');
      const result = await workspace.fetch(tab.id, offset, pageSize, grid);
      if (current()) ctx.updateTab(tab.id, { error: '', result: { ...result, sql } });
    } catch (error) {
      if (current()) ctx.updateTab(tab.id, { error: ctx.message(error) });
    } finally {
      if (paging.get(tab.id) === request) paging.delete(tab.id);
    }
  };
}

export async function fetchViewResult(workspace: WorkspaceApi, id: string, sql: string, queryId: string, display: ResultDisplayPreferences, grid: GridState) {
  const pageSize = consoleView(sql).kind !== 'table' ? 1000 : display.rowSizing === 'fixed' ? display.fixedPageSize : 100;
  const result = await workspace.fetch(id, 0, pageSize, grid);
  return result.query_id === queryId ? { ...result, sql } : undefined;
}
