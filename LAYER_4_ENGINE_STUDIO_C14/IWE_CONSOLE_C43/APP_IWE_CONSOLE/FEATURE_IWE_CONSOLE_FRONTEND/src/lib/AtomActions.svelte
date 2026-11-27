<script lang="ts">
  import { untrack } from 'svelte';
  import AtomLink from './AtomLink.svelte';
  import { atomTextParts, type AtomDocumentData, type AtomDestination } from './console_document';
  import { artifactRef, availableStatuses, DraftSave, lifecycleResult } from './console_lifecycle';
  let { document, call, load, onChanged, onReload, onOpen, register }: {
    document: AtomDocumentData; call: (name: string, args: Record<string, unknown>) => Promise<unknown>;
    load: (ref: string) => Promise<AtomDocumentData>; onChanged: (ref: string) => void;
    onReload: (document: AtomDocumentData) => void;
    onOpen: (ref: string, destination: AtomDestination) => void;
    register?: (flush: () => Promise<boolean>, dirty: () => boolean) => () => void;
  } = $props();
  let editor = $state<DraftSave>(); let revision = $state(0); let error = $state('');
  let busy = $state(false); let reloadNeeded = $state(false); let hidden = $state<string[]>([]); let targetStatus = $state(''); let publishedReady = $state('');
  const key = (r: { type: string; ref_id: string }) => `${r.type}\u0000${r.ref_id}`;
  let draft = $derived(document.status.toLowerCase() === 'draft');
  let options = $derived(availableStatuses(document));
  let view = $derived.by(() => { void revision; return editor ? {
    body: editor.body, dirty: editor.dirty, saving: editor.saving, error: editor.error, conflicted: editor.conflicted,
  } : undefined; });
  export async function flush() { return editor ? editor.flush() : true; }
  $effect(() => register?.(flush, () => !!editor && (editor.dirty || editor.saving)));
  $effect(() => {
    const source = document;
    const next = untrack(() => new DraftSave(source, call, () => { revision++; }));
    editor = next; hidden = []; error = ''; publishedReady = ''; reloadNeeded = false;
    targetStatus = untrack(() => options[0] ?? '');
    return () => next.dispose();
  });
  async function reloadDraft() {
    const current = editor;
    if (!current || current.saving) return;
    busy = true; error = ''; reloadNeeded = true;
    const pending = new Set(current.removed.map(key));
    current.discard();
    hidden = hidden.filter((entry) => !pending.has(entry));
    try {
      const latest = await load(document.exact_ref);
      if (latest?.exact_ref !== document.exact_ref || latest.ref_id !== document.ref_id
        || latest.version !== document.version || typeof latest.status !== 'string' || latest.status.toLowerCase() !== 'draft'
        || typeof latest.updated_at !== 'string' || !latest.updated_at || typeof latest.body !== 'string'
        || !Array.isArray(latest.history) || !Array.isArray(latest.relations) || !Array.isArray(latest.contained)
        || (latest.authored_relations !== undefined && !Array.isArray(latest.authored_relations))) {
        throw new Error('Invalid Draft reload response');
      }
      if (editor === current) onReload(latest);
    } catch (e) { error = e instanceof Error ? e.message : 'Could not reload Draft'; }
    finally { busy = false; }
  }
  async function openDraft() {
    busy = true; error = '';
    try {
      const existing = document.history.find((entry) => entry.status.toLowerCase() === 'draft');
      if (existing) onOpen((await load(existing.ref_id)).exact_ref, 'modal');
      else onOpen(artifactRef(lifecycleResult(await call('atom_lifecycle_create_draft', {
        sourceCurrent: { ref_id: document.ref_id, version: document.version },
      }))), 'modal');
    } catch (e) { error = e instanceof Error ? e.message : 'Could not open Draft'; }
    finally { busy = false; }
  }
  async function transition() {
    busy = true; error = '';
    try {
      if (draft && editor && !await editor.flush()) return;
      const activate = draft && document.ref_id.includes('-S-') && targetStatus === 'active';
      const result = lifecycleResult(await call(draft ? 'atom_lifecycle_promote_draft' : 'atom_lifecycle_change_status', {
        target: { ref_id: draft ? document.exact_ref : document.ref_id, version: document.version },
        targetStatus: activate ? 'ready' : targetStatus,
      }));
      let ref = artifactRef(result);
      if (activate) {
        publishedReady = ref;
        ref = artifactRef(lifecycleResult(await call('atom_lifecycle_change_status', {
          target: { ref_id: document.ref_id, version: document.version }, targetStatus: 'active',
        })));
      }
      onChanged(ref);
    } catch (e) { error = e instanceof Error ? e.message : 'Status change failed'; }
    finally { busy = false; }
  }
</script>

<section aria-label="Atom lifecycle">
  {#if publishedReady}
    <p>Draft published as Ready.</p>
    <button type="button" disabled={busy} onclick={() => onOpen(publishedReady, 'modal')}>Open Current</button>
  {:else if draft && view}
    <label>Body <textarea value={view.body} oninput={(event) => editor?.edit(event.currentTarget.value)} disabled={busy || reloadNeeded}></textarea></label>
    {#each (document.authored_relations ?? []).filter((r) => !hidden.includes(key(r))) as relation}
      <div>{relation.type}: {#if atomTextParts(relation.ref_id)[0]?.ref === relation.ref_id}
        <AtomLink refId={relation.ref_id} {onOpen} />{:else}{relation.ref_id}{/if}
        <button type="button" aria-label={`Remove ${relation.type} ${relation.ref_id}`} disabled={busy || reloadNeeded} onclick={() => { editor?.remove({ type: relation.type, ref_id: relation.ref_id }); hidden = [...hidden, key(relation)]; }}>×</button>
      </div>
    {/each}
    <button type="button" disabled={busy || view.saving || view.conflicted || !view.dirty} onclick={() => editor?.save()}>Save now</button>
    <span>{reloadNeeded || (!view.dirty && view.conflicted) ? 'Reload Draft before saving' : view.saving ? 'Saving…' : view.dirty ? 'Unsaved changes' : 'Saved'}</span>
    {#if view.error}<p role="alert">{view.error}</p>{/if}
    {#if view.dirty || view.conflicted || reloadNeeded}
      <button type="button" disabled={busy || view.saving} onclick={reloadDraft}>{view.dirty ? 'Discard changes and reload' : 'Reload Draft'}</button>
    {/if}
  {:else if !draft && document.status.toLowerCase() !== 'archived'}
    <button type="button" disabled={busy} onclick={openDraft}>Edit Draft</button>
  {/if}
  {#if options.length && !publishedReady}
    <label>Status <select bind:value={targetStatus} disabled={busy || reloadNeeded || !!view?.conflicted}>
      {#each options as status}
        <option value={status}>{status[0].toUpperCase() + status.slice(1).replaceAll('_', ' ')}</option>
      {/each}
    </select></label>
    <button type="button" disabled={busy || reloadNeeded || !!view?.conflicted} onclick={transition}>{draft ? 'Promote Draft' : 'Change status'}</button>
  {/if}
  {#if error}<p role="alert">{error}</p>{/if}
</section>
<style>
  section { display: grid; gap: .5rem; padding: .75rem; border-top: 1px solid #aaa; }
  label { display: grid; gap: .25rem; }
  textarea { min-height: 14rem; width: 100%; font: inherit; }
</style>
