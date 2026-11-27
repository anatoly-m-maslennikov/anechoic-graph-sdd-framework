<script lang="ts">
  import ConsoleGraph from './ConsoleGraph.svelte';
  import ConsoleStructure from './ConsoleStructure.svelte';
  import DocumentStack from './DocumentStack.svelte';
  import { atomTextParts, type AtomActionsSnippet, type AtomDestination,
    type AtomDocumentData } from './console_document';
  import type { ConsoleView } from './console_sql';
  import type { QueryResult } from './types';

  let { result, view, load, query, onOpen, actions }: {
    result: QueryResult; view: ConsoleView;
    load: (ref: string) => Promise<AtomDocumentData>;
    query: (sql: string) => Promise<QueryResult>;
    onOpen: (ref: string, destination: AtomDestination) => void;
    actions: AtomActionsSnippet;
  } = $props();
  function resultRefs(data: QueryResult) {
    const columns = data.columns.map((_, index) => data.rows.flatMap((row) => {
      const value = row[index];
      return typeof value === 'string' && atomTextParts(
        value)[0]?.ref === value ? [value] : [];
    }));
    const candidates = columns.filter((column) => column.length);
    return { refs: candidates[0] ?? [], ambiguous: candidates.length > 1 };
  }
  let occurrenceIndex = $derived(result.columns.findIndex(
    ({ name }) => name === 'occurrence_key'));
  let importOccurrences = $derived(result.rows.flatMap((row) => typeof row[
    occurrenceIndex] === 'string' ? [row[occurrenceIndex]] : []));
  let selection = $derived(resultRefs(result));
</script>

<div class="console-results">
  {#if view.kind === 'structure'}
    <ConsoleStructure {result} {onOpen} />
  {:else if view.kind === 'imports'}
    {#if occurrenceIndex < 0}
      <p role="alert">Select the occurrence_key column to display imports.</p>
    {:else}
      <ConsoleGraph refs={[]} imports {importOccurrences}
        layout={view.layout} {query} {onOpen} />
    {/if}
  {:else if selection.ambiguous}
    <p role="alert">Select a single Atom reference column for this view.</p>
  {:else if selection.refs.length === 0}
    <p>No Atom references in the result.</p>
  {:else if view.kind === 'document'}
    <DocumentStack refs={selection.refs} {load} {onOpen} {actions} />
  {:else if view.kind === 'graph'}
    <ConsoleGraph refs={selection.refs}
      layout={view.layout} {query} {onOpen} />
  {/if}
  {#if result.has_more}<p>
    Showing the first {result.rows.length} rows. Narrow the SQL query to see a
      smaller result.</p>{/if}
</div>

<style>
  .console-results { padding: .5rem; min-width: 0; grid-column: 1 / -1; }
</style>
