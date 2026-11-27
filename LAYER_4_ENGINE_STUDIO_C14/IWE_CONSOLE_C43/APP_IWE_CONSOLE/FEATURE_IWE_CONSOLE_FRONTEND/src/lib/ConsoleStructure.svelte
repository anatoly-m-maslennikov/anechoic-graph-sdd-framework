<script lang="ts">
  import AtomLink from './AtomLink.svelte';
  import { structureEntries } from './console_structure';
  import { atomTextParts, type AtomDestination } from './console_document';
  import type { QueryResult } from './types';
  let { result, onOpen }: { result: QueryResult; onOpen: (ref:
    string, destination: AtomDestination) => void } = $props();
  let entries = $derived(structureEntries(result));
</script>

{#if result.has_more || result.offset > 0}
  <p>Structure is partial. Load all rows to see the full hierarchy.</p>
{/if}
{#if entries.length === 0}
  <p>No Structure entries in this result.</p>
{:else}
  <ul aria-label="Project Structure">
    {#each entries as entry (entry.id)}
      <li style:padding-left="{entry.depth * 1.5}rem">
        <strong>{entry.name}</strong> <span>({entry.id}, {entry.kind})</span>
        {#if entry.purpose}<p>{#each atomTextParts(
          entry.purpose) as part}{#if part.ref}
          <AtomLink refId={part.ref}
            {onOpen} />{:else}{part.text}{/if}{/each}</p>{/if}
        <div>
          {#if entry.manifest}<AtomLink refId={entry.manifest}
            label="Manifest" {onOpen} />{/if}
          {#each entry.solutions as solution}
            {' '}<AtomLink refId={solution} label="Solution" {onOpen} />
          {/each}
        </div>
      </li>
    {/each}
  </ul>
{/if}

<style>
  ul { list-style: none; padding: 0; }
  li { padding-top: .6rem; padding-bottom: .6rem;
    border-bottom: 1px solid var(--border, #ddd); }
  p { margin: .3rem 0; white-space: pre-wrap; }
</style>
