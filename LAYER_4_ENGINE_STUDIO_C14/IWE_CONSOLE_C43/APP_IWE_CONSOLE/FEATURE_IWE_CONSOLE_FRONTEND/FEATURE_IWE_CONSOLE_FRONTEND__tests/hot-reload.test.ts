import assert from 'node:assert/strict';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { loadConfigFromFile } from 'vite';

const configFile = fileURLToPath(new URL('../vite.config.ts',
  import.meta.url));
const root = dirname(configFile);

test('Vite keeps code hot reload disabled even with the retired switch',
  async () => {
  const previous = process.env.ANECHOIC_HOT_RELOAD;
  try {
    process.env.ANECHOIC_HOT_RELOAD = '1';
    for (const mode of ['development', 'mcp-app']) {
      const disabled = await loadConfigFromFile({ command: 'serve', mode },
        configFile, root);
      assert.ok(disabled);
      assert.equal(disabled.config.server?.hmr, false);
      assert.equal(disabled.config.server?.watch, null);
    }
  } finally {
    if (previous === undefined) delete process.env.ANECHOIC_HOT_RELOAD;
    else process.env.ANECHOIC_HOT_RELOAD = previous;
  }
});
