<script lang="ts">
  import { editConsoleSql } from './console_sql';
  let { sql, onChange, disabled = false }: { sql: string; disabled?
    : boolean; onChange: (sql: string) => void } = $props();
  let component = $state(''); let tier = $state(''); let template =
    $state(''); let limit = $state(''); let error = $state('');
  function apply(field:
    'component' | 'tier' | 'template' | 'limit', value: string) {
    try { onChange(editConsoleSql(sql, field, value)); error = ''; }
    catch (cause) { error = cause instanceof Error ?
      cause.message : String(cause); }
  }
</script>
<div class="sql-builder" aria-label="SQL builder">
  <label>Component <input {disabled} bind:value={component}
    onchange={() => apply('component', component)} /></label>
  <label>Tier <input {disabled} bind:value={tier}
    onchange={() => apply('tier', tier)} /></label>
  <label>Template <input {disabled} bind:value={template}
    onchange={() => apply('template', template)} /></label>
  <label>Limit <input {disabled} bind:value={limit}
    onchange={() => apply('limit', limit)} /></label>
</div>
{#if error}<p role="alert">{error}</p>{/if}
<style>
  .sql-builder { display: flex; flex-wrap: wrap; gap: .5rem; }
  label { display: flex; align-items: center; gap: .25rem; }
  input { width: 7rem; }
</style>
