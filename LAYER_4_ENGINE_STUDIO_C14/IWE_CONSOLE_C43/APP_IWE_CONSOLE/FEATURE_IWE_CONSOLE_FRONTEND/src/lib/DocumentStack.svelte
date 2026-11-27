<script lang="ts">
  import { untrack } from 'svelte';
  import AtomDocument from './AtomDocument.svelte';
  import type { AtomActionsSnippet, AtomDestination, AtomDocumentData } from './console_document';
  let { refs, load, onOpen, actions }: {
    refs: string[];
    load: (ref: string) => Promise<AtomDocumentData>;
    onOpen: (ref: string, destination: AtomDestination) => void;
    actions?: AtomActionsSnippet;
  } = $props();
  let items = $state<{ key: string; ref: string; document?: AtomDocumentData; error?: string; expanded: boolean }[]>([]);
  $effect(() => {
    const requested = refs.map((ref, index) => ({ ref, key: `${index}:${ref}` }));
    const loader = load;
    const previous = untrack(() => new Map(items.map((item) => [item.key, item])));
    items = requested.map((item) => previous.get(item.key) ?? { ...item, expanded: true });
    for (const { key, ref } of requested) {
      if (previous.has(key)) continue;
      Promise.resolve().then(() => loader(ref)).then((document) => {
        const item = items.find((entry) => entry.key === key);
        if (item) item.document = document;
      }, (error: unknown) => {
        const item = items.find((entry) => entry.key === key);
        if (item) item.error = error instanceof Error ? error.message : String(error);
      });
    }
  });
  function setExpanded(expanded: boolean) { for (const item of items) item.expanded = expanded; }
</script>

<div class="document-stack">
  <div class="stack-controls">
    <button type="button" onclick={() => setExpanded(false)}>Hide all</button>
    <button type="button" onclick={() => setExpanded(true)}>Expand all</button>
  </div>
  {#each items as item (item.key)}
    <section class="stack-item">
      {#if item.document}
        <button class="heading" type="button" aria-expanded={item.expanded} onclick={() => item.expanded = !item.expanded}>{item.document.filename}</button>
        <div hidden={!item.expanded}><AtomDocument document={item.document} {onOpen} {actions} /></div>
      {:else if item.error}
        <p>Could not load {item.ref}: {item.error}</p>
      {:else}
        <p>Loading {item.ref}…</p>
      {/if}
    </section>
  {/each}
</div>

<style>
  .stack-controls { display: flex; gap: .5rem; }
  .stack-item { border-bottom: 1px solid #8886; padding: .5rem 0; }
  .heading { font: inherit; font-weight: bold; text-align: left; }
</style>
