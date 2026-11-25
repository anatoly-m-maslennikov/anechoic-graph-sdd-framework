import { createServer } from 'vite';

export async function loadLib() {
  const server = await createServer({
    server: { middlewareMode: true, hmr: false },
    ssr: { noExternal: ['tabulator-tables'] },
    plugins: [{
      name: 'test-tabulator', enforce: 'pre',
      resolveId: (id) => id === 'tabulator-tables' ? '\0test-tabulator' : null,
      load: (id) => id === '\0test-tabulator' ? 'export class TabulatorFull {}' : null,
    }],
  });
  try {
    const lib = await server.ssrLoadModule('/src/lib/lib__shared.ts');
    const { render } = await server.ssrLoadModule('svelte/server');
    const { performAction } = await server.ssrLoadModule('/src/app_actions.ts');
    return { ...lib, render, performAction };
  }
  finally { await server.close(); }
}
