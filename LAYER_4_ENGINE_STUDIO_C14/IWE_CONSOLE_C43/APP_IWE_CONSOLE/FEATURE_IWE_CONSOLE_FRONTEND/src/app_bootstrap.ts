import { migrateLegacyDraft, readConsoleStorage,
  restore } from './lib/lib__shared';
import type { NativeBootstrap, WorkspaceApi,
  WorkspaceState } from './lib/lib__shared';
import type { Tab } from './app_actions';
import type { standaloneContext } from './standalone_context';

export async function bindWorkspace(options: {
  api: WorkspaceApi; native?: NativeBootstrap;
    standalone?: ReturnType<typeof standaloneContext>;
  applyBinding(state: WorkspaceState): void;
    applyState(state: WorkspaceState): void;
  updateTab(id: string, changes: Partial<Tab>): void;
  browserStorage<T>(read: () => T): T | undefined;
}) {
  const { api, native, standalone, applyBinding,
    applyState, updateTab, browserStorage } = options;
  const state = native?.workspace ?? (standalone?.standaloneBinding ?
    await api.open() : await api.get());
  applyBinding(state);
  if (!standalone?.standaloneBinding) return;
  const { legacyNamespace, legacySessionId,
    migrationKey, migrationProgressKey } = standalone;
  const allowLegacy = legacySessionId === api.workspaceId;
  const draft = restore(browserStorage(() => readConsoleStorage(
    localStorage, legacyNamespace, !legacySessionId || allowLegacy)) ?? '');
  if (!draft) return;
  const storage = {
    getItem: (key: string) => readConsoleStorage(
      localStorage, key, allowLegacy),
    setItem: (key: string, value: string) => localStorage.setItem(key, value),
  };
  if (storage.getItem(migrationKey) === 'done') return;
  const migrated = await migrateLegacyDraft({ draft, state, api,
    storage, doneKey: migrationKey, progressKey: migrationProgressKey });
  applyState(migrated.state as WorkspaceState);
  for (const source of draft.tabs) {
    const target = migrated.sourceToTarget[source.id];
    if (target) updateTab(target, {
      sql: source.sql, cursor: source.cursor, dirty: source.dirty,
        savedSql: source.savedSql ?? source.sql, syncDirty: false,
    });
  }
}

export function monitorWorkspace(options: {
  persist: () => void; dirty: () => boolean;
    ready: () => boolean; openCommands: () => void;
  sync: () => Promise<void>; refreshStatus: () =>
    Promise<void>; refreshWorkspace: () => Promise<void>;
}) {
  const { persist, dirty, ready, openCommands, sync,
    refreshStatus, refreshWorkspace } = options;
  const unload = (event: BeforeUnloadEvent) => { persist(); if (
    dirty()) { event.preventDefault(); event.returnValue = ''; } };
  const keys = (event: KeyboardEvent) => {
    if (ready() && event.metaKey && !event.ctrlKey &&
      !event.altKey && event.key.toLowerCase() === 'p') {
      event.preventDefault();
      openCommands();
    }
  };
  const catchUpSync = () => { if (ready()) void sync(); };
  window.addEventListener('beforeunload', unload);
  window.addEventListener('pagehide', persist);
  window.addEventListener('keydown', keys, true);
  window.addEventListener('focus', catchUpSync);
  document.addEventListener('visibilitychange', catchUpSync);
  const timer = window.setInterval(() => {
    persist();
    if (ready()) { void refreshStatus();
      void sync(); void refreshWorkspace(); }
  }, 5000);
  return () => {
    window.clearInterval(timer);
    window.removeEventListener('beforeunload', unload);
    window.removeEventListener('pagehide', persist);
    window.removeEventListener('keydown', keys, true);
    window.removeEventListener('focus', catchUpSync);
    document.removeEventListener('visibilitychange', catchUpSync);
  };
}
