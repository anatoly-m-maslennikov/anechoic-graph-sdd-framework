import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
let root = here;
while (!root.endsWith('/LAYER_4_ENGINE_STUDIO_C14')) {
  const parent = dirname(root);
  if (parent === root) throw new Error('Engine root not found');
  root = parent;
}
const frontend = join(root, 'IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND');
const require = createRequire(join(frontend, 'package.json'));
const { transform } = require('esbuild');
const observations = [];

for (const version of ['before', 'fixed']) {
  const source = await readFile(join(here, `${version}.ts.txt`), 'utf8');
  const { code } = await transform(source, { loader: 'ts', format: 'esm' });
  const { performAction } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
  for (const kind of ['run', 'save']) {
    for (const queryId of ['run-1', 'run-2', undefined]) {
      let tab = { id: 'a', sql: 'SELECT 1' };
      let accepted;
      let fetches = 0;
      let refreshed = false;
      const ctx = {
        active: tab, workspaceReady: true, savedBusy: false,
        boundApi: {
          run: async () => ({ status: 'success', revision: 1, query_id: queryId, save_error: 'Save refused' }),
          fetch: async () => { fetches++; return { query_id: 'run-2', rows: [[1]] }; },
        },
        updateTab: (_id, changes) => { tab = { ...tab, ...changes }; },
        fail: (_id, error) => { throw error; }, syncBeforeRun: async () => true, tabById: () => tab,
        message: String, acceptResult: (_id, result) => { accepted = result; },
        acceptSaved: () => assert.fail('Unexpected save'), refreshSaved: async () => { refreshed = true; },
        reportLogWarning: () => {}, resetGrid: () => {},
        resultDisplay: () => ({ rowSizing: 'fixed', fixedPageSize: 25 }), grid: () => ({}),
      };
      await performAction(ctx, kind, 0);
      observations.push({ version, kind, queryId, accepted: accepted?.query_id });
      assert.equal(fetches, queryId ? 1 : 0);
      assert.equal(refreshed, kind === 'save');
      assert.equal(tab.saveError, 'Save refused');
      if (queryId === 'run-2' || (version === 'before' && queryId === 'run-1')) {
        assert.equal(accepted.query_id, 'run-2');
      } else {
        assert.equal(accepted, undefined);
        assert.equal(tab.busy, false);
        if (version === 'fixed') assert.equal(tab.error, queryId
          ? 'The View result changed before it could be displayed.' : 'The completed query has no result ID.');
      }
    }
  }
}
if (process.argv.includes('--observations')) console.log(JSON.stringify(observations));
