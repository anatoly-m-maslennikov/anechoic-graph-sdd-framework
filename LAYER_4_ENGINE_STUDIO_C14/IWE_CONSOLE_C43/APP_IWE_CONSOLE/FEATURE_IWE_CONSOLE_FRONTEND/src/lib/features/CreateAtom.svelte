<script lang="ts">
  import { artifactRef, lifecycleResult } from './console_lifecycle';
  let { call, onCreated }: { call: (name: string, args: Record<string,
    unknown>) => Promise<unknown>; onCreated:
      (ref: string) => void } = $props();
  let template = $state('task'); let lens =
    $state('SPEC'); let tier = $state('2');
  let open = $state(false);
  let component = $state(''); let body = $state('## Summary\n\n');
    let busy = $state(false); let error = $state('');
  async function create() {
    busy = true; error = '';
    try {
      const result = lifecycleResult(await call(
        'atom_lifecycle_create_draft', {
        newAtom: template === 'task' || template === 'epic'
          ? { template, container: { component: component.trim() }, body }
          : { template, container: { component: 'C00' },
            lens: template === 'axiom' ? 'SPEC' : lens.trim(),
              ...(template === 'applicable_principle' ?
                { tier: Number(tier) } : {}), body },
      }));
      const ref = artifactRef(result);
      open = false;
      onCreated(ref);
    } catch (e) { error = e instanceof Error ? e.message : 'Creation failed'; }
    finally { busy = false; }
  }
</script>
<details bind:open>
<summary>Create Atom</summary>
<form onsubmit={(event) => { event.preventDefault(); void create(); }}>
  <label>Template <select bind:value={template} disabled={busy}>
    <option value="task">Task</option><option value="epic">Epic</option>
    <option value="axiom">Axiom</option><option
      value="applicable_principle">Applicable Principle</option>
    <option value="project_contract">Project Contract</option>
  </select></label>
  {#if template === 'task' || template === 'epic'}
    <label>Component <input bind:value={component}
      placeholder="C00" required disabled={busy} /></label>
  {:else}
    <span>Container: C00</span>
    {#if template !== 'axiom'}<label>Lens <input
      bind:value={lens} required disabled={busy} /></label>{/if}
    {#if template === 'applicable_principle'}<label>Tier <select
      bind:value={tier}
      disabled={busy}><option value="1">1</option><option
        value="2">2</option></select></label>{/if}
  {/if}
  <label>Body <textarea bind:value={body}
    required disabled={busy}></textarea></label>
  <button type="submit" disabled={busy}>Create Draft</button>
  {#if error}<p role="alert">{error}</p>{/if}
</form>
</details>
<style>
  form, label { display: grid; gap: .5rem; }
  textarea { min-height: 8rem; font: inherit; }
</style>
