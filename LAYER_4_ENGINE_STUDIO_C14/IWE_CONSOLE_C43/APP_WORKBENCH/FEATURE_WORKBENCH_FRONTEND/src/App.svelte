

<script lang="ts">
  import { onMount } from 'svelte';
  import { standaloneContext } from './standalone_context';
  import { performAction, synchronizeDraft, gridColumn, gridRow, type Tab } from './app_actions';
  import { Button, CommandPalette, NameDialog, OpenSavedDialog, Preferences, ResultsTable, SavedPanel, SqlEditor, SyncStatus, ViewTabs } from './lib/lib__shared';
  import { WorkbenchApi, WorkspaceApi, migrateLegacyDraft, formatSql, cleanAfterSave, newView, persistable, restore, storageKey, workspaceTabs } from './lib/lib__shared';
  import type { Command, PreferenceCommand, NativeBootstrap, OperationCaller, GridState, QueryLogItem, QueryResult, ResultDisplayPreferences, SavedIdentity, SavedItem, Schema, SourceSyncStatus, WorkspaceState, WorkspaceView } from './lib/lib__shared';

  const props: { caller: OperationCaller; native?: NativeBootstrap } = $props();
  const caller = props.caller;
  const native = props.native;
  let browserStorageUnavailable = $state(false);
  function browserStorage<T>(operation: () => T): T | undefined {
    if (browserStorageUnavailable) return;
    try { return operation(); } catch { browserStorageUnavailable = true; }
  }
  const standalone = native === undefined ? standaloneContext(browserStorage) : undefined;
  let projectName = $state('');
  const workspaceId = native?.sessionId ?? standalone!.workspaceId;
  const embedded = native !== undefined || standalone?.embedded === true;
  const standaloneBinding = standalone?.standaloneBinding ?? false;
  const namespace = native ? storageKey(native.workspace.project_name, native.sessionId, native.projectRoot) : standalone!.namespace;
  const legacyNamespace = standalone?.legacyNamespace ?? '';
  const migrationKey = standalone?.migrationKey ?? '';
  const migrationProgressKey = standalone?.migrationProgressKey ?? '';
  const initial = newView(1) as Tab;
  let tabs = $state<Tab[]>([initial]); let activeId = $state(initial.id); let view = $state<'settings' | 'saved' | 'view'>('view');
  let schema = $state<Schema>({ tables: {} }); let savedItems = $state<SavedItem[]>([]); let logItems = $state<QueryLogItem[]>([]); let syncStatus = $state<SourceSyncStatus>({ mode: 'unavailable' }); let storageError = $state(''); let collapsed = $state(false);
  let workspaceReady = $state(false); let savedBusy = $state(false); let openSavedDialog = $state(false); let commandOpen = $state(false); let nameDialog = $state<{ kind: 'save' | 'rename'; id?: string; initialValue: string } | null>(null);
  let preferenceCommands = $state<PreferenceCommand[]>([]); let api: WorkbenchApi; let boundApi: WorkspaceApi | undefined; const syncing = new Map<string, Promise<boolean>>(); const paging = new Map<string, number>(); let pageRequest = 0;
  let resultDisplay = $state<ResultDisplayPreferences>({ rowSizing: 'adaptive', fixedPageSize: 100, content: 'limited', contentLimit: 150 }); let grid = $state<GridState>({ sort: [], filters: [] }); let gridLayoutVersion = $state(0); let adaptedGeometry = $state('');
  let active = $derived(tabs.find((tab) => tab.id === activeId)); let commands = $derived(buildCommands());
  let check = $derived(active?.check && active.check.sql === active.sql ? active.check : undefined);

  const message = (error: unknown) => error instanceof Error ? error.message : 'Request failed';
  function tabById(id: string) { return tabs.find((tab) => tab.id === id); }
  function tabName(tab: Tab) { return tab.name || tab.title; }
  function updateTab(id: string, changes: Partial<Tab>) { tabs = tabs.map((tab) => tab.id === id ? { ...tab, ...changes } : tab); }
  function persist() { if (!native && projectName) browserStorage(() => localStorage.setItem(namespace, persistable(tabs, activeId))); }
  function fail(id: string, error: unknown, conflict = false) { updateTab(id, { busy: false, error: message(error), ...(conflict ? { conflict: true } : {}) }); }
  function edit(sql: string, cursor: number) {
    if (!active || (active.sql === sql && active.cursor === cursor)) return;
    updateTab(active.id, { sql, cursor, dirty: sql !== active.savedSql, syncDirty: true, conflict: false, error: '', ...(active.sql !== sql ? { check: undefined, saveError: undefined } : {}) });
  }
  function formatActive() {
    const tab = active;
    if (!workspaceReady || !tab || tab.busy || savedBusy) return;
    try {
      const formatted = formatSql(tab.sql);
      edit(formatted, Math.min(tab.cursor, formatted.length));
    } catch (error) { updateTab(tab.id, { error: message(error) }); }
  }
  function showView(id: string) {
    if (view === 'view' && activeId === id) return;
    activeId = id; view = 'view'; grid = { sort: [], filters: [] }; fetchRemoteResult(id);
    if (boundApi) void boundApi.focus(id).then(({ active_view_id }) => activeId = active_view_id).catch((error) => fail(id, error));
  }
  function showUtility(next: 'settings' | 'saved') { view = next; if (next === 'saved') void refreshSaved(); }
  function applyServerView(server: WorkspaceView, replace = false) {
    const current = tabById(server.id); if (!current) return;
    if (!replace && (current.syncDirty || current.dirty) && server.sql !== current.sql) {
      updateTab(server.id, { ...(server.name === undefined ? { name: undefined } : { name: server.name }), run: server.result, serverSql: server.sql, serverRevision: server.revision });
      return;
    }
    updateTab(server.id, {
      ...(server.name === undefined ? { name: undefined } : { name: server.name }), revision: server.revision, run: server.result,
      ...(replace ? { sql: server.sql, savedSql: server.sql, cursor: server.cursor_position, dirty: false, syncDirty: false, conflict: false, result: undefined, check: undefined, serverSql: undefined, serverRevision: undefined } : {}),
    });
  }
  function fetchRemoteResult(id: string) {
    const tab = tabById(id); const queryId = tab?.run?.query_id;
    if (!boundApi || !tab || !queryId || tab.result?.query_id === queryId) return;
    void boundApi.fetch(id, 0, resultDisplay.rowSizing === 'fixed' ? resultDisplay.fixedPageSize : 100, grid).then((result) => { if (tabById(id)?.run?.query_id === queryId) updateTab(id, { result, error: '' }); }).catch((error) => fail(id, error));
  }
  function applyState(state: WorkspaceState) {
    const merged = workspaceTabs(state, tabs); tabs = merged.tabs as Tab[]; activeId = merged.activeId ?? activeId;
    const current = tabById(activeId);
    if (current?.run?.status === 'failed') updateTab(current.id, { error: current.run.error || 'Query failed' });
    else if (current) fetchRemoteResult(current.id);
  }
  function applyBinding(state: WorkspaceState) {
    if (typeof state.project_name !== 'string' || !state.project_name.trim()) {
      workspaceReady = false;
      throw new Error('Workspace binding requires the Project name.');
    }
    projectName = state.project_name;
    applyState(state);
  }
  async function refreshWorkspace() {
    if (!boundApi) return;
    try { applyBinding(await boundApi.get()); } catch (error) { storageError = message(error); }
  }
  async function migrateUnboundDraft(state: WorkspaceState, draft: ReturnType<typeof restore>) {
    if (!boundApi || !standaloneBinding || !draft || localStorage.getItem(migrationKey) === 'done') return;
    const migrated = await migrateLegacyDraft({ draft, state, api: boundApi, storage: localStorage, doneKey: migrationKey, progressKey: migrationProgressKey });
    applyState(migrated.state as WorkspaceState);
    for (const source of draft.tabs) {
      const target = migrated.sourceToTarget[source.id];
      if (target) updateTab(target, { sql: source.sql, cursor: source.cursor, dirty: source.dirty, savedSql: source.savedSql ?? source.sql, syncDirty: false });
    }
  }
  async function rebuildResults() {
    const target = window.prompt('Table selector or all', 'all');
    if (target === null) return;
    try {
      storageError = '';
      await api.rebuild(target.trim());
      if (boundApi) {
        const state = await boundApi.get();
        applyBinding(state);
      }
    } catch (error) { storageError = message(error); }
  }
  async function refreshStatus() { try { syncStatus = await api.status(); } catch { syncStatus = { ...syncStatus, mode: 'unavailable' }; } }
  function syncDraft(id: string) {
    return synchronizeDraft({ syncing, tabById, boundApi, fail, updateTab }, id);
  }
  async function syncBeforeRun(id: string) {
    const pending = syncing.get(id); if (pending && !await pending) return false;
    return !tabById(id)?.syncDirty || await syncDraft(id);
  }
  async function flushDrafts() { for (const tab of tabs) if (tab.syncDirty && !tab.busy && !tab.conflict) await syncDraft(tab.id); }
  async function addView(position: 'first' | 'last' = 'last') {
    if (!workspaceReady || !boundApi) { storageError = 'Workspace is unavailable.'; return; }
    try { const state = await boundApi.create(position); applyState(state); showView(state.view_id); } catch (error) { storageError = message(error); }
  }
  async function duplicateView(id = active?.id) {
    const source = id ? tabById(id) : undefined;
    if (!workspaceReady || !boundApi || !source || source.busy || savedBusy) return;
    if (!await syncBeforeRun(source.id) || tabById(source.id)?.syncDirty || tabById(source.id)?.conflict) return;
    try {
      const state = await boundApi.duplicate(source.id);
      applyState(state);
      if (!tabById(state.view_id)) throw new Error('Duplicated View is unavailable.');
      updateTab(state.view_id, { savedSql: '', dirty: true, syncDirty: false, saved: undefined, result: undefined, check: undefined, run: undefined, error: '' });
      showView(state.view_id);
    }
    catch (error) { fail(source.id, error); }
  }
  function renameActiveView() {
    if (active) requestRename(active.id);
  }
  function requestRename(id: string) { const tab = tabById(id); if (!tab) return; showView(id); nameDialog = { kind: 'rename', id, initialValue: tabName(tab) }; }
  function submitName(name: string) { const request = nameDialog; nameDialog = null; if (request?.kind === 'rename' && request.id) void renameView(request.id, name); else void action('save', active?.cursor, name); }
  async function renameView(id: string, name: string) {
    if (!boundApi) { storageError = 'Workspace is unavailable.'; return; }
    try { applyServerView(await boundApi.rename(id, name.trim()), false); } catch (error) { fail(id, error); }
  }
  async function closeView(id: string) {
    const tab = tabById(id); if (!tab || (tab.dirty && !confirm(`Close unsaved ${tabName(tab)}?`))) return;
    if (!boundApi) { storageError = 'Workspace is unavailable.'; return; }
    if (tabs.length === 1) { fail(id, new Error('The last View cannot be removed.')); return; }
    try { await boundApi.remove(id); await refreshWorkspace(); } catch (error) { fail(id, error); }
  }
  function acceptSaved(id: string, saved: SavedIdentity) {
    const current = tabById(id); if (!current) return;
    updateTab(id, { ...(cleanAfterSave(current, saved.sql) as Tab), syncDirty: false, saved, busy: false, error: '' });
  }
  function acceptResult(id: string, result: QueryResult) { updateTab(id, { result, busy: false, error: '' }); }
  function reportLogWarning(id: string, warning?: string) { if (warning) updateTab(id, { error: `${tabById(id)?.error ? `${tabById(id)!.error} ` : ''}Query log warning: ${warning}` }); }
  function savedFrom(result: QueryResult): SavedIdentity | undefined {
    return result.saved_query_id && result.saved_query_url && result.kind === 'query' ? { saved_query_id: result.saved_query_id, saved_query_url: result.saved_query_url, kind: result.kind, sql: result.sql, ...(result.name ? { name: result.name } : {}) } : undefined;
  }
  function action(kind: 'run' | 'check' | 'save', cursor = active?.cursor ?? 0, name?: string) {
    return performAction({ active, workspaceReady, savedBusy, boundApi, updateTab, fail, syncBeforeRun, tabById, message, acceptResult, acceptSaved, refreshSaved, reportLogWarning,
      resetGrid: () => grid = { sort: [], filters: [] }, resultDisplay: () => resultDisplay, grid: () => grid }, kind, cursor, name);
  }
  function requestSave() { if (workspaceReady && active && !active.busy) nameDialog = { kind: 'save', initialValue: '' }; }
  async function saveView(name = active?.name) {
    const tab = active; if (!workspaceReady || !tab || tab.busy || savedBusy) return;
    updateTab(tab.id, { busy: true, error: '', saveError: undefined });
    if (!boundApi) { fail(tab.id, new Error('Workspace is unavailable.')); return; }
    if (!await syncBeforeRun(tab.id)) { updateTab(tab.id, { busy: false }); return; }
    try { const saved = await boundApi.save(tab.id); acceptSaved(tab.id, { ...saved, sql: tabById(tab.id)?.sql ?? tab.sql, ...(name ? { name } : {}) }); await refreshSaved(); } catch (error) { updateTab(tab.id, { busy: false, saveError: message(error) }); }
  }
  async function page(offset: number, pageSize = active?.result?.page_size, nextGrid = grid) {
    const tab = active; if (!tab?.result || tab.busy) return;
    const queryId = tab.result.query_id;
    const request = ++pageRequest; paging.set(tab.id, request);
    try {
      if (!boundApi || !pageSize) throw new Error('Workspace is unavailable.');
      const result = await boundApi.fetch(tab.id, offset, pageSize, nextGrid);
      const latest = tabById(tab.id);
      if (paging.get(tab.id) === request && !latest?.busy && latest?.result?.query_id === queryId) updateTab(tab.id, { error: '', result });
    } catch (error) {
      const latest = tabById(tab.id);
      if (paging.get(tab.id) === request && !latest?.busy && latest?.result?.query_id === queryId) updateTab(tab.id, { error: message(error) });
    }
    finally { if (paging.get(tab.id) === request) paging.delete(tab.id); }
  }
  function setResultDisplay(next: ResultDisplayPreferences) {
    const sizingChanged = next.rowSizing !== resultDisplay.rowSizing || next.fixedPageSize !== resultDisplay.fixedPageSize;
    resultDisplay = next; if (sizingChanged) gridLayoutVersion += 1;
    if (next.rowSizing === 'fixed' && active?.result) void page(active.result.offset, next.fixedPageSize);
  }
  function setGrid(next: GridState) { grid = next; if (active?.result) void page(0, active.result.page_size, next); }
  function adaptPage(size: number, geometry: string) {
    const result = active?.result; if (!result || resultDisplay.rowSizing !== 'adaptive') return;
    const key = `${result.query_id}:${gridLayoutVersion}:${JSON.stringify(grid)}:${geometry}`;
    if (adaptedGeometry === key || result.page_size === size) return;
    adaptedGeometry = key; void page(result.offset, size);
  }
  async function refreshSaved() {
    try { savedItems = (await api.savedList()).items; } catch (error) { storageError = message(error); }
    try { if (boundApi) logItems = (await boundApi.queryLogList()).items; }
    catch (error) { storageError = message(error); }
  }
  async function openLog(logId: string) { if (!boundApi) return; try { const item = await boundApi.queryLogGet(logId); storageError = `${item.outcome}: ${item.row_count ?? 'unknown'} rows, ${item.column_count ?? 'unknown'} columns${item.error ? ` — ${item.error}` : ''}`; } catch (error) { storageError = message(error); } }
  async function openSaved(reference: string) {
    if (savedBusy) return; savedBusy = true;
    try {
      const saved = await api.load(reference);
      if (!boundApi) throw new Error('Workspace is unavailable.');
      const existing = tabs.filter((tab) => tab.saved?.saved_query_id === saved.saved_query_id).find((tab) => tab.id === activeId) ?? tabs.find((tab) => tab.saved?.saved_query_id === saved.saved_query_id);
      if (existing) { showView(existing.id); openSavedDialog = false; return; }
      const state = await boundApi.create('last', saved.name); applyState(state); const server = state.views.find((item) => item.id === state.view_id); if (!server) throw new Error('Created View is unavailable');
      applyServerView(await boundApi.update(server.id, saved.sql, server.revision, 0), true); showView(server.id); updateTab(server.id, { saved });
      openSavedDialog = false;
    } catch (error) { storageError = message(error); } finally { savedBusy = false; }
  }
  function savedLink(event: MouseEvent, id: string) {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    showView(id);
  }
  function focusSql() { view = 'view'; collapsed = false; requestAnimationFrame(() => document.querySelector<HTMLElement>('.cm-content')?.focus()); }
  function focusResults() { view = 'view'; requestAnimationFrame(() => document.querySelector<HTMLElement>('.results-panel')?.focus()); }
  function resultValue(value: unknown) { if (value === null) return 'NULL'; try { return typeof value === 'object' ? JSON.stringify(value) : String(value); } catch { return String(value); } }
  function copyResult(value: unknown) { void navigator.clipboard?.writeText(resultValue(value)).catch(() => {}); }
  function filterGrid() { const column = gridColumn(active); if (column < 0) return; const value = window.prompt(`Filter ${active!.result!.columns[column].name}`, grid.filters.find((item) => item.column === column)?.value ?? ''); if (value === null) return; const filters = grid.filters.filter((item) => item.column !== column); if (value) filters.push({ column, operator: 'contains', value }); setGrid({ ...grid, filters }); }
  function buildCommands(): Command[] {
    const busy = !workspaceReady || !active || active.busy || savedBusy; const result = active?.result;
    return [
      { id: 'settings', label: 'Settings', enabled: true, run: () => showUtility('settings') }, { id: 'saved', label: 'Bookmarks and saved Views', enabled: true, run: () => showUtility('saved') },
      ...(native || syncStatus.mode === 'startup_snapshot' ? [{ id: 'rebuild-results', label: 'Rebuild tables', enabled: workspaceReady, run: rebuildResults }] : []),
      { id: 'open', label: 'Open Saved', enabled: !savedBusy, run: () => openSavedDialog = true }, { id: 'focus-sql', label: 'Focus Query editor', enabled: !!active, run: focusSql }, { id: 'focus-results', label: 'Focus Results', enabled: !!result, run: focusResults },
      ...tabs.map((tab) => ({ id: `view-${tab.id}`, label: `View: ${tabName(tab)}`, enabled: workspaceReady, run: () => showView(tab.id) })), { id: 'new-first', label: 'New View first', enabled: workspaceReady, run: () => addView('first') }, { id: 'new-last', label: 'New View last', enabled: workspaceReady, run: () => addView('last') },
      { id: 'rename', label: 'Rename View', enabled: workspaceReady && !!active, run: renameActiveView }, { id: 'duplicate', label: 'Duplicate View', enabled: workspaceReady && !!active && !active.busy && !savedBusy, run: () => active && duplicateView(active.id) }, { id: 'close', label: 'Close View', enabled: workspaceReady && !!active, run: () => active && closeView(active.id) },
      { id: 'run', label: 'Run', shortcut: 'Cmd+Enter', enabled: !busy, run: () => action('run') }, { id: 'check', label: 'Check', shortcut: 'Shift+Cmd+Enter', enabled: !busy, run: () => action('check') }, { id: 'format', label: 'Format', enabled: !busy, run: formatActive }, { id: 'save', label: 'Run & Save', enabled: !busy, run: requestSave }, { id: 'save-view', label: 'Save View', enabled: !busy, run: () => saveView() },
      { id: 'hide', label: collapsed ? 'Show editor' : 'Hide editor', enabled: !!active, run: () => collapsed = !collapsed }, { id: 'previous-page', label: 'Previous result page', enabled: !!result && result.offset > 0 && !busy, run: () => result && page(Math.max(0, result.offset - result.page_size)) }, { id: 'next-page', label: 'Next result page', enabled: !!result?.has_more && !busy, run: () => result && page(result.offset + result.rows.length) },
      { id: 'grid-copy-value', label: 'Result grid: Copy cell value', enabled: !!result, run: () => { const row = gridRow(active); const column = gridColumn(active); if (row >= 0 && column >= 0) copyResult(result!.rows[row][column]); } }, { id: 'grid-show-value', label: 'Result grid: Show full cell value', enabled: !!result, run: () => { const row = gridRow(active); const column = gridColumn(active); if (row >= 0 && column >= 0) window.alert(resultValue(result!.rows[row][column])); } }, { id: 'grid-copy-row', label: 'Result grid: Copy row', enabled: !!result, run: () => { const row = gridRow(active); if (row >= 0) copyResult(result!.rows[row]); } },
      { id: 'grid-sort-asc', label: 'Result grid: Sort column ascending', enabled: !!result, run: () => { const column = gridColumn(active); if (column >= 0) setGrid({ ...grid, sort: [...grid.sort.filter((item) => item.column !== column), { column, direction: 'asc' }] }); } }, { id: 'grid-sort-desc', label: 'Result grid: Sort column descending', enabled: !!result, run: () => { const column = gridColumn(active); if (column >= 0) setGrid({ ...grid, sort: [...grid.sort.filter((item) => item.column !== column), { column, direction: 'desc' }] }); } },
      { id: 'grid-group-asc', label: 'Result grid: Group column ascending', enabled: !!result, run: () => { const column = gridColumn(active); if (column >= 0) setGrid({ ...grid, group_by: { column, direction: 'asc' } }); } }, { id: 'grid-group-desc', label: 'Result grid: Group column descending', enabled: !!result, run: () => { const column = gridColumn(active); if (column >= 0) setGrid({ ...grid, group_by: { column, direction: 'desc' } }); } }, { id: 'grid-clear-group', label: 'Result grid: Clear grouping', enabled: !!grid.group_by, run: () => setGrid({ ...grid, group_by: undefined }) }, { id: 'grid-filter', label: 'Result grid: Filter column', enabled: !!result, run: filterGrid }, { id: 'grid-clear-filter', label: 'Result grid: Clear filter', enabled: grid.filters.length > 0, run: () => setGrid({ ...grid, filters: [] }) },
      ...preferenceCommands.map((command) => ({ ...command, enabled: true })),
    ];
  }
  onMount(() => {
    api = new WorkbenchApi(caller);
    if (!native) {
      const recovered = restore(browserStorage(() => localStorage.getItem(namespace)) ?? '');
      if (recovered) { tabs = recovered.tabs as Tab[]; activeId = recovered.activeId; }
    }
    const initialize = async () => {
      if (!workspaceId) { storageError = 'Workspace binding requires a Workspace ID.'; return; }
      try {
        boundApi = new WorkspaceApi(caller, workspaceId);
        const state = native?.workspace ?? (standaloneBinding ? await boundApi.open() : await boundApi.get());
        applyBinding(state);
        if (standaloneBinding) {
          const draft = restore(browserStorage(() => localStorage.getItem(legacyNamespace)) ?? '');
          await migrateUnboundDraft(state, draft);
        }
      } catch (error) {
        if (error instanceof DOMException && ['SecurityError', 'QuotaExceededError'].includes(error.name)) browserStorageUnavailable = true;
        else storageError = message(error);
        if (!projectName) return;
      }
      workspaceReady = true;
      void refreshStatus(); void api.schema().then((value) => schema = value).catch(() => {}); await refreshSaved(); const requested = standalone?.parameters.get('query'); if (requested) await openSaved(requested);
    };
    void initialize();
    const unload = (event: BeforeUnloadEvent) => { persist(); if (tabs.some((tab) => tab.dirty)) { event.preventDefault(); event.returnValue = ''; } };
    const keys = (event: KeyboardEvent) => { if (workspaceReady && event.metaKey && !event.ctrlKey && !event.altKey && event.key.toLowerCase() === 'p') { event.preventDefault(); nameDialog = null; openSavedDialog = false; commandOpen = true; } };
    const catchUpSync = () => { if (workspaceReady) void flushDrafts(); };
    window.addEventListener('beforeunload', unload); window.addEventListener('pagehide', persist); window.addEventListener('keydown', keys, true);
    window.addEventListener('focus', catchUpSync); document.addEventListener('visibilitychange', catchUpSync);
    const timer = window.setInterval(() => { persist(); if (workspaceReady) { void refreshStatus(); void flushDrafts(); void refreshWorkspace(); } }, 5000);
    return () => { window.clearInterval(timer); window.removeEventListener('beforeunload', unload); window.removeEventListener('pagehide', persist); window.removeEventListener('keydown', keys, true); window.removeEventListener('focus', catchUpSync); document.removeEventListener('visibilitychange', catchUpSync); };
  });
</script>

<main class="workbench"><header class="app-header"><span class="brand-mark">CA</span><span class="app-name">Workbench</span>{#if projectName}<span class="project-label">Project: {projectName}</span>{/if}<div class="header-right"><SyncStatus status={syncStatus} /><div class="header-utilities" role="tablist" aria-label="Workbench views"><button class:active={view === 'settings'} type="button" role="tab" aria-selected={view === 'settings'} onclick={() => showUtility('settings')}>Settings</button><button class:active={view === 'saved'} type="button" role="tab" aria-label="Bookmarks and saved Views" title="Bookmarks and saved Views" aria-selected={view === 'saved'} onclick={() => showUtility('saved')}>Saved</button></div></div></header><section class="workspace"><div class="work-main">
  <div class="workspace-toolbar"><div class="toolbar-main"><ViewTabs {tabs} {activeId} utility={view} ready={workspaceReady} onselect={showView} onclose={closeView} onadd={addView} onrenamerequest={requestRename} onduplicate={duplicateView} /></div><div class="toolbar-actions"><Button disabled={!workspaceReady} onclick={() => commandOpen = true}>Commands <span class="shortcut">Cmd+P</span></Button></div></div>
  {#if browserStorageUnavailable}<p class="error" role="alert">Browser storage is unavailable. Reloading or closing Workbench may lose unsaved edits.</p>{/if}
  <Preferences storageKey={namespace} {embedded} visible={view === 'settings'} {resultDisplay} onresultdisplaychange={setResultDisplay} onlayoutchange={() => gridLayoutVersion += 1} oncommands={(items) => preferenceCommands = items} />
  {#if view === 'saved'}<SavedPanel items={savedItems} logs={logItems} busy={savedBusy} onopen={openSaved} onopenlog={openLog} />{/if}
  {#if view === 'view' && active}<section class="editor-panel"><div class="panel-heading"><button class="editor-heading" type="button" aria-expanded={!collapsed} aria-controls={`query-editor-${active.id}`} onclick={() => collapsed = !collapsed}><span>Query editor</span><span class="editor-heading-state">{collapsed ? 'Show editor' : 'Hide editor'}</span></button>{#if active.saved}<span class="saved-reference">Saved: <a href={active.saved.saved_query_url} onclick={(event) => savedLink(event, active.id)}>{active.saved.saved_query_id}</a></span>{/if}</div><div class="editor-content" id={`query-editor-${active.id}`} hidden={collapsed}>{#key active.id}<SqlEditor value={active.sql} cursor={active.cursor} disabled={!workspaceReady || active.busy} {schema} onchange={edit} onaction={(kind, cursor) => action(kind, cursor)} />{/key}</div><div class="query-actions"><Button disabled={!workspaceReady || active.busy || savedBusy} onclick={() => action('run')}>Run <span class="shortcut">Cmd+Enter</span></Button><Button disabled={!workspaceReady || active.busy || savedBusy} onclick={() => action('check')}>Check <span class="shortcut">Shift+Cmd+Enter</span></Button><Button disabled={!workspaceReady || active.busy || savedBusy} onclick={formatActive}>Format</Button><Button disabled={!workspaceReady || active.busy || savedBusy} onclick={requestSave}>Run &amp; Save</Button><Button disabled={!workspaceReady || active.busy || savedBusy} onclick={() => saveView()}>Save View</Button></div>
    {#if active.error}<p class="error" role="alert">{active.error}</p>{/if}
    {#if active.saveError}<p class="error" role="alert">{active.saveError}</p>{/if}
  </section>
    <section class="results-panel" tabindex="-1"><div class="status-line"><span class="status-badge">{active.busy ? 'Working' : 'Ready'}</span><span class="notice" role="status" aria-label="Query check">
      {#if !check}Not checked{:else if 'error' in check}Invalid: {check.error}{:else if check.result.valid}Valid: {check.result.row_count} rows, {check.result.column_count} columns.{:else}Invalid{/if}
    </span></div>{#if active.result}<ResultsTable result={active.result} display={resultDisplay} {grid} layoutVersion={gridLayoutVersion} ondisplaychange={setResultDisplay} ongridchange={setGrid} oncapacity={adaptPage} /><nav class="query-actions" aria-label="Result pages"><Button disabled={active.busy || active.result.offset === 0} onclick={() => page(Math.max(0, active.result!.offset - active.result!.page_size))}>Previous</Button><Button disabled={active.busy || !active.result.has_more} onclick={() => page(active.result!.offset + active.result!.rows.length)}>Next</Button></nav>{/if}</section>{/if}
  {#if storageError}<p class="error" role="alert">{storageError}</p>{/if}
</div></section></main>
<OpenSavedDialog open={openSavedDialog} busy={savedBusy} onopen={openSaved} onclose={() => openSavedDialog = false} />
<NameDialog open={nameDialog !== null} title={nameDialog?.kind === 'rename' ? 'View name' : 'Bookmark name'} initialValue={nameDialog?.initialValue ?? ''} onsubmit={submitName} onclose={() => nameDialog = null} />
<CommandPalette open={commandOpen} {commands} onclose={() => commandOpen = false} />
