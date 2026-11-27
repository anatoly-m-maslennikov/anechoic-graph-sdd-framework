<script lang="ts">
  import { onMount } from 'svelte';
  import AtomDocument from './AtomDocument.svelte';
  import type { AtomActionsSnippet, AtomDestination, AtomDocumentData } from './console_document';

  let { refId, load, onOpen, onClose, actions }: {
    refId: string; load: (ref: string) => Promise<AtomDocumentData>;
    onOpen: (ref: string, destination: AtomDestination) => void;
    onClose: () => void; actions: AtomActionsSnippet;
  } = $props();
  let dialog: HTMLDialogElement;
  onMount(() => dialog.showModal());
</script>

<dialog bind:this={dialog} aria-label="Atom document" oncancel={(event) => { event.preventDefault(); onClose(); }}>
  <div class="modal-actions">
    <button type="button" onclick={() => onOpen(refId, 'pane')}>Open in pane</button>
    <button type="button" onclick={() => onOpen(refId, 'tab')}>Open in new tab</button>
    <button type="button" onclick={onClose}>Close</button>
  </div>
  {#await load(refId)}
    <p role="status">Loading {refId}…</p>
  {:then atom}
    <AtomDocument document={atom} {onOpen} {actions} />
  {:catch error}
    <p role="alert">{error instanceof Error ? error.message : String(error)}</p>
  {/await}
</dialog>

<style>
  dialog { width: min(72rem, 94vw); max-height: 90vh; background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: .5rem; }
  dialog::backdrop { background: #0007; }
  .modal-actions { display: flex; gap: .5rem; margin-bottom: 1rem; }
</style>
