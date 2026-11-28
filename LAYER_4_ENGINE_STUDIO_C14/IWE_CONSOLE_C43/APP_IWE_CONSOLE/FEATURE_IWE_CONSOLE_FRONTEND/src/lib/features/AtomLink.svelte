<script lang="ts">
  import { tick } from 'svelte';
  import type { AtomDestination } from './console_document';
  let { refId, label, onOpen }: {
    refId: string; label?: string;
    onOpen: (ref: string, destination: AtomDestination) => void;
  } = $props();
  let menu = $state(false);
  let trigger: HTMLButtonElement;
  let firstItem = $state<HTMLButtonElement>();
  async function openMenu() {
    menu = true;
    await tick();
    if (menu) firstItem?.focus();
  }
  function escapeMenu(event: KeyboardEvent) {
    if (menu && event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      menu = false;
      trigger.focus();
    }
  }
  function choose(destination: AtomDestination) {
    menu = false;
    onOpen(refId, destination);
  }
</script>

<svelte:window onclick={() => { menu = false; }} onkeydown={escapeMenu} />

<span class="atom-link">
  <button bind:this={trigger} class="link"
    type="button" onclick={() => choose('modal')}
    oncontextmenu={(event) => { event.preventDefault(); void openMenu(); }}
    onkeydown={(event) => {
      if (event.key === 'ContextMenu' || (event.shiftKey
        && event.key === 'F10')) {
        event.preventDefault(); void openMenu();
      }
    }}
    aria-haspopup="menu" aria-expanded={menu}>{label ?? refId}</button>
  {#if menu}
    <span class="menu" role="menu" tabindex="-1">
      <button bind:this={firstItem} type="button" role="menuitem"
        onclick={() => choose('modal')}>Open in modal</button>
      <button type="button" role="menuitem"
        onclick={() => choose('pane')}>Open in pane</button>
      <button type="button" role="menuitem"
        onclick={() => choose('tab')}>Open in tab</button>
      <button type="button" role="menuitem"
        onclick={() => { menu = false; }}>Cancel</button>
    </span>
  {/if}
</span>

<style>
  .atom-link { position: relative; display: inline; }
  .link { padding: 0; border: 0; background: none;
    color: var(--accent, #4178be); text-decoration: underline;
      cursor: pointer; font: inherit; }
  .menu { position: absolute; z-index: 20; top: 100%; left: 0; display: grid;
    min-width: 9rem; padding: .25rem; background: var(--surface, white);
      border: 1px solid #888; box-shadow: 0 2px 8px #0003; }
  .menu button { text-align: left; white-space: nowrap; }
</style>
