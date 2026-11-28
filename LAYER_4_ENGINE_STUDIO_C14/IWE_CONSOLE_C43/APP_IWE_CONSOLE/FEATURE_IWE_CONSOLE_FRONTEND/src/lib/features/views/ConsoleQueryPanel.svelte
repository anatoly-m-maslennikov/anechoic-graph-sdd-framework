<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Button } from '../controls/controls__shared';
  import ConsoleResults from './ConsoleResults.svelte';
  import { CreateAtom } from '../features__shared';
  import { DocumentStack } from '../features__shared';
  import ResultsTable from './ResultsTable.svelte';
  import { SqlBuilder } from '../controls/controls__shared';
  import { consoleView, type ConsoleView } from './console_sql';
  import type { ConsoleNavigation } from './console_navigation.svelte';
  import type { AtomActionsSnippet } from '../features__shared';
  import type { CheckResult, GridState, QueryResult,
    ResultDisplayPreferences } from '../../lib__shared';

  let { id, sql, result, check, busy, ready, collapsed, nav, editor,
    atomActions, query, onBuilderChange, selectView, display, grid,
    layoutVersion, setResultDisplay, setGrid, adaptPage, page }: {
    id: string; sql: string; result?: QueryResult; check?
      : { result: CheckResult } | { error: string };
    busy?: boolean; ready: boolean; collapsed: boolean; nav: ConsoleNavigation;
    editor: Snippet; atomActions: AtomActionsSnippet;
    query: (sql: string) => Promise<QueryResult>;
      onBuilderChange: (sql: string) => void;
    selectView: (kind: ConsoleView['kind']) => void;
      display: ResultDisplayPreferences; grid: GridState;
    layoutVersion: number; setResultDisplay: (
      display: ResultDisplayPreferences) => void;
    setGrid: (grid: GridState) => void; adaptPage:
      (size: number, geometry: string) => void;
    page: (offset: number) => void;
  } = $props();
  let selection = $derived(consoleView(sql));
  let presentation = $derived(consoleView(result?.sql || sql));
  let pane = $derived(nav.panes[id]);
</script>

<div class:split-console={pane?.length}>
  <div class="query-pane">
    <section class="editor-panel">
      {@render editor()}
      {#if !collapsed}
        {#key id}
          <div class="console-filters">
            <SqlBuilder {sql} disabled={!ready || busy}
              onChange={onBuilderChange} />
            <label>View <select value={selection.kind}
              disabled={!ready || busy}
              onchange={(event) => selectView(
                event.currentTarget.value as ConsoleView['kind'])}>
              <option value="table">Table</option>
              <option value="document">Document</option>
              <option value="graph">Graph</option>
              <option value="imports">Imports</option>
              <option value="structure">Structure</option>
            </select></label>
            {#if ready}<CreateAtom call={nav.call}
              onCreated={(ref) => nav.open(ref, 'modal')} />{/if}
          </div>
        {/key}
      {/if}
    </section>
    <section class="results-panel" tabindex="-1">
      <div class="status-line"><span
        class="status-badge">{busy ? 'Working' : 'Ready'}</span><span
        class="notice" role="status" aria-label="Query check">
        {#if !check}Not checked{:else if 'error' in check}Invalid:
          {check.error}{:else if check.result.valid}Valid:
            {check.result.row_count} rows, {check.result.column_count}
              columns.{:else}Invalid{/if}
      </span></div>
      {#if result}
        {#if presentation.kind === 'table'}
          <ResultsTable {result} {busy} {display}
            {grid} {layoutVersion} onOpen={nav.open}
            ondisplaychange={setResultDisplay}
              ongridchange={setGrid} oncapacity={adaptPage} />
          <nav class="query-actions" aria-label="Result pages">
            <Button disabled={busy || result.offset === 0}
              onclick={() => page(Math.max(0,
                result!.offset - result!.page_size))}>Previous</Button>
            <Button disabled={busy || !result.has_more}
              onclick={() => page(result!.offset
                + result!.rows.length)}>Next</Button>
          </nav>
        {:else}
          {#key nav.generation}
            <ConsoleResults {result} view={presentation} load={nav.load}
              query={query} onOpen={nav.open} actions={atomActions} />
          {/key}
        {/if}
      {/if}
    </section>
  </div>
  {#if pane?.length}
    <aside class="atom-pane" aria-label="Atom document pane">
      <button type="button" onclick={nav.closePane}>Close pane</button>
      {#key `${id}:${nav.generation}`}
        <DocumentStack refs={pane} load={nav.load}
          onOpen={nav.open} actions={atomActions} />
      {/key}
    </aside>
  {/if}
</div>

<style>
  .console-filters { grid-column: 1 / -1; display: flex; gap: .5rem;
    flex-wrap: wrap; padding: .5rem; }
  .query-pane { min-width: 0; }
  .split-console { display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(15rem, 2fr); gap: .5rem; }
  .atom-pane { min-width: 0; padding: .5rem; max-height: 85vh; overflow: auto;
    border: 1px solid var(--border); }
  @media (max-width: 48rem) { .split-console {
    grid-template-columns: minmax(0, 1fr); } }
</style>
