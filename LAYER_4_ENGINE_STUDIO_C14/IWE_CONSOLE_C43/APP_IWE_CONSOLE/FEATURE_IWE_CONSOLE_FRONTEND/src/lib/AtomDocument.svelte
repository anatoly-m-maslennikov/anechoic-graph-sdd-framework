<script lang="ts">
  import AtomLink from './AtomLink.svelte';
  import { atomTextParts, type AtomActionsSnippet, type AtomDestination,
    type AtomDocumentData } from './console_document';
  let { document: source, onOpen, actions }: {
    document: AtomDocumentData;
    onOpen: (ref: string, destination: AtomDestination) => void;
    actions?: AtomActionsSnippet;
  } = $props();
  let reloaded = $state.raw<{ source:
    AtomDocumentData; latest: AtomDocumentData }>();
  let document = $derived(reloaded?.source === source ?
    reloaded.latest : source);
  function reload(latest: AtomDocumentData) { reloaded = { source, latest }; }
</script>

<article class="atom-document">
  <header>
    <strong>{document.filename}</strong>
    <span><AtomLink refId={document.exact_ref}
      {onOpen} /> · {document.status}</span>
    {#if document.template}<span>Template: {document.template}</span>{/if}
    {#if document.updated_at}<span>Updated: {document.updated_at}</span>{/if}
    {#if document.archive_pending}<span>Archive pending</span>{/if}
    {#if actions}{@render actions(document, reload)}{/if}
  </header>
  <div
    class="body">{#each atomTextParts(
      document.body) as part}{#if part.ref}<AtomLink
    refId={part.ref} {onOpen} />{:else}{part.text}{/if}{/each}</div>
  {#if document.history.length}
    <section><h4>History</h4><ul>
      {#each document.history as item}
        <li><AtomLink refId={item.ref_id} label={item.filename}
          {onOpen} /> · {item.status} · {item.version}</li>
      {/each}
    </ul></section>
  {/if}
  {#if document.relations.length}
    <section><h4>Relations</h4><ul>
      {#each document.relations as relation}
        <li>{relation.type} ({relation.direction}{relation.derived
          ? ', derived' : ''}):
          {#if atomTextParts(relation.ref_id)[0]?.ref === relation.ref_id}
            <AtomLink refId={relation.ref_id}
              {onOpen} />{:else}{relation.ref_id}{/if}
        </li>
      {/each}
    </ul></section>
  {/if}
  {#if document.contained.length}
    <section><h4>Contained</h4><ul>
      {#each document.contained as item}
        <li><AtomLink refId={item.ref_id}
          label={item.filename} {onOpen} /></li>
      {/each}
    </ul></section>
  {/if}
</article>

<style>
  header { display: flex; flex-wrap: wrap; gap: .5rem; align-items: baseline; }
  .body { white-space: pre-wrap; overflow-wrap: anywhere; margin: 1rem 0; }
  h4 { margin: .7rem 0 .2rem; }
  ul { margin: 0; padding-left: 1.5rem; }
</style>
