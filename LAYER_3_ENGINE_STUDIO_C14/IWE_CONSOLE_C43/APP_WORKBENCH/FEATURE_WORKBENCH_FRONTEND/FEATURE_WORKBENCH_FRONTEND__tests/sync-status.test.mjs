import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'vite';

test('source index status distinguishes native, unavailable, and legacy states', async () => {
  const server = await createServer({ server: { middlewareMode: true } });
  try {
    const { default: SyncStatus } = await server.ssrLoadModule('/src/lib/SyncStatus.svelte');
    const { render } = await server.ssrLoadModule('svelte/server');
    for (const [status, text] of [
      [{ mode: 'startup_snapshot' }, 'Startup snapshot'],
      [{ mode: 'live_index' }, 'Watching files'],
      [{ mode: 'unavailable', syncing: false }, 'Unavailable'],
      [{ syncing: true, last_synced_at: null }, 'Syncing'],
      [{ syncing: false, last_synced_at: null }, 'Not synced yet'],
      [{ syncing: false, last_synced_at: '2026-01-01T00:00:00Z' }, new Date('2026-01-01T00:00:00Z').toLocaleString()],
    ]) {
      assert.match(render(SyncStatus, { props: { status } }).body, new RegExp(`Source index: ${text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
    }
  } finally {
    await server.close();
  }
});
