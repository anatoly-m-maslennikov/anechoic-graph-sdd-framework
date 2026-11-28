<script lang="ts">
  import { AtomLink } from './features/features__shared';
  import type { AtomDestination } from './features/features__shared';
  import type { SourceSyncStatus } from './types';
  let { status, rebuild, onOpen }: {
    status: SourceSyncStatus; rebuild: (target: string) => Promise<unknown>;
    onOpen: (ref: string, destination: AtomDestination) => void;
  } = $props();
  let running = $state('');
  let result = $state('');
  let error = $state('');
  async function run(target: string, label: string) {
    running = label; result = ''; error = '';
    try { await rebuild(target); result = `${label} complete.`; }
    catch (cause) { error = cause instanceof Error ?
      cause.message : String(cause); }
    finally { running = ''; }
  }
</script>

<section class="diagnostics" aria-label="Diagnostics">
  <h2>Project diagnostics</h2>
  <dl>
    <dt>Runtime</dt><dd>{status.health?.state === 'ready' ? 'Healthy'
      : status.health?.state === 'pending' ? 'Starting' : status.health
        || status.mode === 'unavailable' ? 'Unhealthy' : 'Unknown'}</dd>
    <dt>Index</dt><dd>{status.syncing ? 'Updating'
      : status.mode === 'live_index' ? 'Available'
        : status.mode === 'startup_snapshot' ? 'Starting' : 'Unavailable'}</dd>
    <dt>Last sync</dt><dd>{status.last_synced_at ?? 'Unknown'}</dd>
    <dt>Archive</dt><dd>{status.archive?.state ?? 'Unknown'}</dd>
    <dt>Watcher events queued</dt><dd>{status.watcher_queue_depth
      ?? 'Unknown'}</dd>
    {#if status.indexed_atom_count !== undefined}
      <dt>Indexed Atoms</dt><dd>{status.indexed_atom_count}</dd>
    {/if}
    {#if status.worker_runs}
      <dt>Active Workers</dt><dd>{status.worker_runs.active.length}</dd>
    {/if}
    <dt>Worker outcomes</dt><dd>{status.worker_runs
      ? status.worker_runs.latest.map(run =>
          `${run.kind.replaceAll('_', ' ')} · ${run.status}`).join(', ')
        || 'None'
      : status.last_run_state ?? 'Unknown'}</dd>
    <dt>Ingestion issues</dt><dd>{status.ingestion_issue_count
      ?? status.ingestion_issues?.length
      ?? 'Unknown'}</dd>
  </dl>
  {#if status.health?.error?.message}<p
    role="status">{status.health.error.message}</p>{/if}
  {#if status.ingestion_issues?.length}
    <details><summary>Ingestion issues</summary>
      <ul>{#each status.ingestion_issues as issue}<li>
        {#if issue.atom_ref}<AtomLink refId={issue.atom_ref} {onOpen} />{/if}
        {issue.message ?? issue.code ?? issue.relative_path
          ?? 'Ingestion issue'}
      </li>{/each}</ul>
    </details>
  {/if}
  <button type="button" disabled={!!running}
    onclick={() => run('realization_graph',
      'Realization Graph rebuild')}>Rebuild Realization Graph</button>
  <button type="button" disabled={!!running}
    onclick={() => run('all',
      'Project database rebuild')}>
        Rebuild Project database from source</button>
  {#if running}<p role="status">{running} in progress…</p>{/if}
  {#if result}<p role="status">{result}</p>{/if}
  {#if error}<p role="alert">{error}</p>{/if}
</section>

<style>
  .diagnostics { padding: .75rem; }
  dl { display: grid; grid-template-columns: max-content 1fr;
    gap: .25rem .75rem; }
  dd { margin: 0; }
</style>
