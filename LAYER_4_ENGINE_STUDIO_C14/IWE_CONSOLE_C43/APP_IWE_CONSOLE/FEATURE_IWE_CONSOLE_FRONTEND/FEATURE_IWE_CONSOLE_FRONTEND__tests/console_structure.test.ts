import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { loadLib } from './FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';
const { structureEntries } = await loadLib();
import type { QueryResult } from '../src/lib/lib__shared';

test('orders children under parents and preserves purpose and links', () => {
  const columns = ['id', 'parent', 'kind', 'name', 'purpose', 'manifest', 'solutions']
    .map(name => ({ name, type: 'VARCHAR' }));
  const result = { columns, rows: [
    ['CS1', 'C2', 'Component Seed', 'CS1', 'Seed purpose', 'AN-S-2', 'AN-S-2'],
    ['C2', 'C00', 'Component', 'Child', 'Component purpose', 'AN-S-1', 'AN-S-3|AN-S-4'],
    ['C00', null, 'Component', 'Project', null, null, null],
  ] } as QueryResult;
  const entries = structureEntries(result);
  assert.deepEqual(entries.map(entry => [entry.id, entry.depth]), [['C00', 0], ['C2', 1], ['CS1', 2]]);
  assert.equal(entries[1].purpose, 'Component purpose');
  assert.deepEqual(entries[1].solutions, ['AN-S-3', 'AN-S-4']);
  assert.deepEqual(entries[2].solutions, ['AN-S-2']);
});
