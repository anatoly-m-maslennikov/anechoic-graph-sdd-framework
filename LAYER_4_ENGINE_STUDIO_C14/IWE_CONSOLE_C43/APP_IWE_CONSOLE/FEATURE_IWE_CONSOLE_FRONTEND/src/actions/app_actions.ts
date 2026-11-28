import type { WorkspaceApi, CheckResult, GridState, QueryResult,
  ResultDisplayPreferences, SavedIdentity,
    ViewResult } from '../lib/lib__shared';
import { newView } from '../lib/lib__shared';
import { consoleView } from '../lib/features/views/views__shared';

export { gridCommands } from './app_grid_commands';

type Check = { sql: string; result:
  CheckResult } | { sql: string; error: string };
export type Tab = Omit<ReturnType<typeof newView>, 'id'> & { id: string; name?:
  string; busy?: boolean; error?: string;
    saveError?: string; result?: QueryResult;
  check?: Check; saved?: SavedIdentity; revision?
    : number; run?: ViewResult; conflict?:
    boolean; syncDirty?: boolean; serverSql?
      : string; serverRevision?: number };
type ActionContext = {
  active: Tab | undefined; workspaceReady: boolean;
    savedBusy: boolean; boundApi: WorkspaceApi | undefined;
  updateTab: (id: string, changes: Partial<Tab>) => void; fail:
    (id: string, error: unknown, conflict?: boolean) => void;
  syncBeforeRun: (id: string) => Promise<boolean>;
    tabById: (id: string) => Tab | undefined;
  message: (error: unknown) => string; acceptResult:
    (id: string, result: QueryResult) => void;
  acceptSaved: (id: string, saved: SavedIdentity) =>
    void; refreshSaved: () => Promise<void>;
  reportLogWarning: (id: string, warning?:
    string) => void; resetGrid: () => void;
  resultDisplay: () => ResultDisplayPreferences; grid: () => GridState;
};

async function checkView(
  ctx: ActionContext, api: WorkspaceApi, tab: Tab, cursor: number,
) {
  const { updateTab, fail, message } = ctx;
  try {
    const result = await api.check(tab.id, cursor);
    updateTab(tab.id, { busy: false, check: { sql: tab.sql, result } });
  } catch (error) {
    if (error instanceof TypeError) fail(tab.id, error);
    else updateTab(tab.id, {
      busy: false, check: { sql: tab.sql, error: message(error) },
    });
  }
}

function recordSaved(
  ctx: ActionContext, tab: Tab,
  response: Awaited<ReturnType<WorkspaceApi['run']>>, name?: string,
) {
  const { acceptSaved } = ctx;
  const { save_error, saved_query_id, saved_query_url } = response;
  if (save_error || !saved_query_id || !saved_query_url) return;
  acceptSaved(tab.id, {
    saved_query_id, saved_query_url, kind: 'query', sql: tab.sql,
    ...(name ? { name } : {}),
  });
}

async function runView(
  ctx: ActionContext, api: WorkspaceApi, tab: Tab, cursor: number,
  save: boolean, name?: string,
) {
  const { updateTab, acceptResult, refreshSaved, reportLogWarning, fail } =
    ctx;
  const { id } = tab;
  try {
    const response = await api.run(id, cursor,
      save ? { save: true, ...(name ? { name } : {}) } : {});
    if (!Number.isInteger(tab.revision) ||
        response.revision !== tab.revision) {
      updateTab(id, { run: undefined, result: undefined });
      throw new Error('The View changed before its query could be displayed.');
    }
    ctx.resetGrid();
    updateTab(id, { revision: response.revision, run: response,
      result: undefined, saveError: response.save_error });
    if (save) {
      recordSaved(ctx, tab, response, name);
      updateTab(id, { busy: true });
    }
    if (response.status === 'failed') {
      updateTab(id, { busy: false, error: response.error || 'Query failed' });
    } else if (typeof response.query_id === 'string' &&
        response.query_id.trim()) {
      const result = await fetchViewResult(
        api, id, tab.sql, response.query_id, ctx.resultDisplay(), ctx.grid(),
      );
      if (result) acceptResult(id, result);
      else updateTab(id, { busy: false,
        error: 'The View result changed before it could be displayed.' });
    } else updateTab(id, {
      busy: false, error: 'The completed query has no result ID.',
    });
    if (save) await refreshSaved();
    reportLogWarning(id, response.query_log_error);
  } catch (error) { fail(id, error); }
}

export async function performAction(
  ctx: ActionContext, kind: 'run' | 'check' | 'save', cursor: number,
  name?: string,
) {
  const { active, workspaceReady, savedBusy, updateTab, boundApi, fail,
    syncBeforeRun, tabById } = ctx;
  const tab = active;
  if (!workspaceReady || !tab || tab.busy || savedBusy) return;
  updateTab(tab.id, { busy: true, error: '', saveError: undefined,
    ...(kind === 'check' ? { check: undefined } : {}) });
  if (!boundApi) {
    fail(tab.id, new Error('Workspace is unavailable.'));
    return;
  }
  if (!await syncBeforeRun(tab.id)) {
    updateTab(tab.id, { busy: false });
    return;
  }
  const current = tabById(tab.id);
  if (!current) return;
  if (current.syncDirty || current.conflict) {
    const error = 'The View changed before its SQL could be submitted.';
    fail(tab.id, new Error(error));
    return;
  }
  if (kind === 'check') return checkView(ctx, boundApi, current, cursor);
  return runView(ctx, boundApi, current, cursor, kind === 'save', name);
}


type SyncContext = {
  syncing: Map<string, Promise<boolean>>;
    tabById: (id: string) => Tab | undefined;
  boundApi: WorkspaceApi | undefined; fail: (id:
    string, error: unknown, conflict?: boolean) => void;
  updateTab: (id: string, changes: Partial<Tab>) => void;
};

export function synchronizeDraft(ctx:
  SyncContext, id: string): Promise<boolean> {
  const { syncing, tabById, boundApi, fail, updateTab } = ctx;
  const pending = syncing.get(id); if (pending) return pending;
  const tab = tabById(id);
  if (!boundApi || !tab?.syncDirty ||
    tab.conflict) return Promise.resolve(!tab?.conflict);
  if (!Number.isInteger(tab.revision)) { fail(id, new Error(
    'View revision is unavailable'), true); return Promise.resolve(false); }
  const submitted = { sql: tab.sql, cursor:
    tab.cursor, revision: tab.revision };
  let request!: Promise<boolean>;
  request = (async () => {
    try {
      const server = await boundApi!.update(id,
        submitted.sql, submitted.revision!, submitted.cursor);
      if (server.id !== id || server.sql !== submitted.sql) throw new Error(
        'The View update receipt did not match the submitted SQL.');
      const latest = tabById(id);
      if (latest && (latest.sql !== submitted.sql ||
        latest.cursor !== submitted.cursor)) {
        updateTab(id, { revision: server.revision,
          run: server.result, check: undefined,
          syncDirty: true, conflict: false, serverSql:
            undefined, serverRevision: undefined });
      } else updateTab(id, { revision:
        server.revision, run: server.result, syncDirty:
        false, conflict: false, serverSql:
          undefined, serverRevision: undefined });
      return true;
    } catch (error) { fail(id, error, true); return false; }
    finally { if (syncing.get(id) === request) syncing.delete(id); }
  })();
  syncing.set(id, request);
  return request;
}

export function resultPager(ctx: {
  workspace: () => WorkspaceApi | undefined; active: () => Tab | undefined;
  tabById: (id: string) => Tab | undefined; updateTab:
    (id: string, changes: Partial<Tab>) => void;
  message: (error: unknown) => string;
}) {
  const paging = new Map<string, number>();
  let pageRequest = 0;
  return async (offset: number, pageSize:
    number | undefined, grid: GridState) => {
    const tab = ctx.active(), workspace = ctx.workspace();
    if (!tab?.result || tab.busy || consoleView(
      tab.result.sql).kind !== 'table') return;
    const { query_id: queryId, sql } = tab.result;
    const request = ++pageRequest;
    paging.set(tab.id, request);
    const current = () => {
      const latest = ctx.tabById(tab.id);
      return paging.get(tab.id) === request &&
        !latest?.busy && latest?.result?.query_id === queryId;
    };
    try {
      if (!workspace || !pageSize) throw new Error(
        'Workspace is unavailable.');
      const result = await workspace.fetch(tab.id, offset, pageSize, grid);
      if (current() && result.query_id === queryId) ctx.updateTab(tab.id, {
        result: { ...result, sql } });
    } catch (error) {
      if (current()) ctx.updateTab(tab.id, { error: ctx.message(error) });
    } finally {
      if (paging.get(tab.id) === request) paging.delete(tab.id);
    }
  };
}

export async function fetchViewResult(workspace: WorkspaceApi, id: string, sql:
  string, queryId: string, display:
    ResultDisplayPreferences, grid: GridState) {
  const pageSize = consoleView(sql).kind !== 'table' ? 1000 :
    display.rowSizing === 'fixed' ? display.fixedPageSize : 100;
  const result = await workspace.fetch(id, 0, pageSize, grid);
  return result.query_id === queryId ? { ...result, sql } : undefined;
}
