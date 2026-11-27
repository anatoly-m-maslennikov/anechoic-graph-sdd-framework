
<script lang="ts">
  import type { SourceSyncStatus } from './types';
  let { status }: { status: SourceSyncStatus } = $props();
  function text() {
    if (status.mode === 'startup_snapshot') return 'Startup snapshot';
    if (status.mode === 'live_index') return 'Watching files';
    if (status.mode === 'unavailable') return 'Unavailable';
    if (status.syncing) return 'Syncing';
    return status.last_synced_at ? new Date(
      status.last_synced_at).toLocaleString() : 'Not synced yet';
  }
</script>

<span class="sync-status" role="status"
  aria-label="Source indexing status">Source index: {text()}</span>
