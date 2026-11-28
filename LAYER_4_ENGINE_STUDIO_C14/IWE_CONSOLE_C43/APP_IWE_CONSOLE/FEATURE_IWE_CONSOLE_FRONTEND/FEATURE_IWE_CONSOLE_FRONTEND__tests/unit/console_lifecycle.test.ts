import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadLib } from '../FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';

const { DraftSave, lifecycleResult } = await loadLib();
import type { AtomDocumentData } from '../../src/lib/features/features__shared';

const doc: AtomDocumentData = { ref_id: 'AN-T-1@2-draft',
  exact_ref: 'AN-T-1@2-draft', version: 2,
  status: 'draft', filename: '', body: 'old', updated_at:
    'one', history: [], relations: [], contained: [] };

test(
  'serializes changes made during a save and advances the expected timestamp',
  async () => {
  const calls: Record<string, unknown>[] = [];
  let release!: (value: unknown) => void;
  const draft = new DraftSave(doc, async (_name, args) => {
    calls.push(args);
    if (calls.length === 1) return new Promise(
      (resolve) => { release = resolve; });
    return { artifact: { updated_at: 'three' } };
  }, () => {});
  draft.edit('first');
  const first = draft.save();
  draft.edit('second');
  const flush = draft.flush();
  assert.equal(calls.length, 1);
  release({ artifact: { updated_at: 'two' } });
  assert.equal(await first, true);
  assert.equal(await flush, true);
  assert.deepEqual(calls.map((call) =>
    call.expectedUpdatedAt), ['one', 'two']);
  assert.deepEqual(calls.map((call) => call.changes),
    [{ body: 'first' }, { body: 'second' }]);
  assert.equal(draft.dirty, false);
  draft.dispose();
});

test('failed saves preserve edits and a retry clears the error', async () => {
  let attempts = 0;
  const draft = new DraftSave(doc, async () => ++attempts === 1
    ? { status: 'failed', errors: [{ message: 'conflict' }] }
    : { artifact: { updated_at: 'two' } }, () => {});
  draft.edit('new'); draft.remove({ type: 'REL', ref_id: 'AN-T-2' });
  assert.equal(await draft.flush(), false);
  assert.equal(draft.error, 'conflict');
  assert.equal(draft.body, 'new');
  assert.equal(draft.dirty, true);
  assert.equal(await draft.flush(), true);
  assert.equal(draft.error, '');
  assert.equal(draft.dirty, false);
  draft.dispose();
  assert.throws(() => lifecycleResult({ status: 'failed' }), /failed/);
});

test('a stale Draft retains edits and stops retrying until the editor reloads',
  async (context) => {
  context.mock.timers.enable({ apis: ['setTimeout'] });
  let attempts = 0;
  const draft = new DraftSave(doc, async () => {
    attempts++;
    return { status: 'failed', errors: [{ code:
      'source_changed', message: 'Draft changed' }] };
  }, () => {});
  const relation = { type: 'REL', ref_id: 'AN-T-2' };
  draft.edit('new'); draft.remove(relation);
  assert.equal(await draft.flush(), false);
  draft.edit('newer');
  context.mock.timers.tick(5000);
  assert.equal(await draft.flush(), false);
  assert.equal(attempts, 1);
  assert.equal(draft.body, 'newer');
  assert.deepEqual(draft.removed, [relation]);
  assert.equal(draft.error, 'Draft changed');
  draft.discard();
  assert.equal(await draft.flush(), true);
  assert.equal(draft.body, 'old');
  assert.deepEqual(draft.removed, []);
  draft.dispose();
});

test('continuous typing does not postpone the five-second save',
  async (context) => {
  context.mock.timers.enable({ apis: ['setTimeout'] });
  const calls: Record<string, unknown>[] = [];
  const draft = new DraftSave(doc, async (_name, args) => {
    calls.push(args);
    return { artifact: { updated_at: 'two' } };
  }, () => {});
  draft.edit('first');
  context.mock.timers.tick(4000);
  draft.edit('second');
  context.mock.timers.tick(1000);
  assert.deepEqual(calls[0].changes, { body: 'second' });
  await draft.flush();
  draft.dispose();
});
