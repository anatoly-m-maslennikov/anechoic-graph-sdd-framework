import type { WorkspaceApi, CheckResult, GridState, QueryResult, ResultDisplayPreferences, SavedIdentity, ViewResult } from './lib/lib__shared';
import { newView } from './lib/lib__shared';

type Check = { sql: string; result: CheckResult } | { sql: string; error: string };
export type Tab = ReturnType<typeof newView> & { busy?: boolean; error?: string; result?: QueryResult; check?: Check; saved?: SavedIdentity; revision?: number; run?: ViewResult; conflict?: boolean; syncDirty?: boolean; serverSql?: string; serverRevision?: number };
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
  updateTab(tab.id, { busy: true, error: '', ...(kind === 'check' ? { check: undefined } : {}) });
  if (!boundApi) { fail(tab.id, new Error('Workspace is unavailable.')); return; }
  if (!await syncBeforeRun(tab.id)) { updateTab(tab.id, { busy: false }); return; }
  const current = tabById(tab.id); if (!current) return;
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
    ctx.resetGrid(); updateTab(current.id, { revision: response.revision, run: response, result: undefined });
    if (response.status === 'failed') updateTab(current.id, { busy: false, error: response.error || 'Query failed' });
    else if (response.query_id) acceptResult(current.id, await boundApi.fetch(current.id, 0, ctx.resultDisplay().rowSizing === 'fixed' ? ctx.resultDisplay().fixedPageSize : 100, ctx.grid()));
    else updateTab(current.id, { busy: false });
    if (kind === 'save') {
      if (response.save_error) updateTab(current.id, { error: response.save_error });
      else if (response.saved_query_id && response.saved_query_url) acceptSaved(current.id, { saved_query_id: response.saved_query_id, saved_query_url: response.saved_query_url, kind: 'query', sql: current.sql, ...(name ? { name } : {}) });
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

export function gridColumn(active: Tab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(`Result column index (0-${result.columns.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) && index >= 0 && index < result.columns.length ? index : -1;
}
export function gridRow(active: Tab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(`Result row index on this page (0-${result.rows.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) && index >= 0 && index < result.rows.length ? index : -1;
}
