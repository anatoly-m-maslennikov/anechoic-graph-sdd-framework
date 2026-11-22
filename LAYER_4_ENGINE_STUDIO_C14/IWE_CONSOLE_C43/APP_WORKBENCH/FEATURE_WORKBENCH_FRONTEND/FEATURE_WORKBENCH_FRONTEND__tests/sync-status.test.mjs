import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadLib } from './FEATURE_WORKBENCH_FRONTEND__tests__shared.mjs';

test('source index status distinguishes native, unavailable, and legacy states', async () => {
  const { SyncStatus, render } = await loadLib();
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
});
