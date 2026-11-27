import { readFileSync } from 'node:fs';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig, type Plugin } from 'vite';

const server = { hmr: false as const, watch: null };
const webBase = '/anechoic/iwe-console/';
const helperNotices = {
  '\0vite/modulepreload-polyfill.js': 'Vite module preload polyfill\n' +
    'Copyright (c) 2019-present, VoidZero Inc. and Vite contributors',
  '\0commonjsHelpers.js': 'Rollup CommonJS helper\n' +
    'Copyright (c) 2019 RollupJS Plugin Contributors ' +
    '(https://github.com/rollup/plugins/graphs/contributors)',
};
const helperLicense = readFileSync(
  new URL('./scripts/build-helper-license.txt', import.meta.url), 'utf8',
);

function bundleLicenses(fileName: string): Plugin {
  return {
    name: 'workbench-bundle-licenses',
    apply: 'build',
    generateBundle: {
      order: 'post',
      handler(_, bundle) {
        const report = bundle[fileName];
        if (report?.type !== 'asset')
          this.error(`Missing bundle license report ${fileName}`);
        const moduleIds = new Set(Object.values(bundle).flatMap((output) =>
          output.type === 'chunk' ? output.moduleIds : []));
        const usedNotices = Object.entries(helperNotices)
          .filter(([id]) => moduleIds.has(id)).map(([, notice]) => notice);
        if (usedNotices.length) {
          report.source = `${report.source}\n## Build helpers (MIT)\n\n` +
            `${usedNotices.join('\n\n')}\n\n${helperLicense}`;
        }
      },
    },
    transformIndexHtml() {
      return [{
        tag: 'footer', attrs: { class: 'third-party-licenses' },
        injectTo: 'body',
        children: [{ tag: 'a', attrs: { href: `${webBase}${fileName}` },
          children: 'Third-party licenses' }],
      }];
    },
  };
}

export default defineConfig(({ mode }) => {
  const mcpApp = mode === 'mcp-app';
  const fileName = mcpApp ? 'THIRD_PARTY_LICENSES.txt' :
    'assets/THIRD_PARTY_LICENSES.txt';
  const build = { emptyOutDir: true, license: { fileName } };
  return {
    server,
    plugins: [svelte(), bundleLicenses(fileName)],
    base: mcpApp ? '/' : webBase,
    build: mcpApp ? {
      ...build,
      outDir: 'dist/.mcp-app-assets', cssCodeSplit: false, sourcemap: false,
      rollupOptions: { input: 'src/mcp-app.ts', output: {
        entryFileNames: 'mcp-app.js', assetFileNames: 'mcp-app.[ext]',
        inlineDynamicImports: true,
      } },
    } : { ...build, outDir: 'dist' },
  };
});
