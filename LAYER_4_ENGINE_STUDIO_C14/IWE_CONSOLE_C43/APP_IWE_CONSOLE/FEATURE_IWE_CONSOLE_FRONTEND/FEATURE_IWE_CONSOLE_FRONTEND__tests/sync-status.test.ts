import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { SourceSyncStatus } from '../src/lib/lib__shared';
import { loadLib } from './FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';

test('source index status distinguishes native, unavailable, and legacy states',
  async () => {
  const { SyncStatus, render } = await loadLib();
  const cases: Array<[SourceSyncStatus, string]> = [
    [{ mode: 'startup_snapshot' }, 'Startup snapshot'],
    [{ mode: 'live_index' }, 'Watching files'],
    [{ mode: 'unavailable', syncing: false }, 'Unavailable'],
    [{ syncing: true, last_synced_at: null }, 'Syncing'],
    [{ syncing: false, last_synced_at: null }, 'Not synced yet'],
    [{ syncing: false, last_synced_at: '2026-01-01T00:00:00Z' },
      new Date('2026-01-01T00:00:00Z').toLocaleString()],
  ];
  for (const [status, text] of cases) {
    assert.match(render(SyncStatus, { props: { status } }).body, new RegExp(
      `Source index: ${text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
  }
});
