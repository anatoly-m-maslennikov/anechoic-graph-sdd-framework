import { createServer } from 'vite';

type WorkbenchLib = typeof import('../src/lib/lib__shared');
type SvelteServer = typeof import('svelte/server');

export async function loadLib() {
  const server = await createServer({
    server: { middlewareMode: true, hmr: false },
    ssr: { noExternal: ['tabulator-tables'] },
    plugins: [{
      name: 'test-tabulator', enforce: 'pre',
      resolveId: (id) => id === 'tabulator-tables' ? '\0test-tabulator' : null,
      load: (id) => id === '\0test-tabulator' ?
        'export class TabulatorFull {}' : null,
    }],
  });
  try {
    const lib = await server.ssrLoadModule(
      '/src/lib/lib__shared.ts') as WorkbenchLib;
    const { render } = await server.ssrLoadModule(
      'svelte/server') as SvelteServer;
    return { ...lib, render };
  }
  finally { await server.close(); }
}
