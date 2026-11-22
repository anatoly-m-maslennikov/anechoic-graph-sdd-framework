import { build } from 'vite';
import { readdir, readFile, rm, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = process.cwd();
const assets = resolve(root, 'dist/.mcp-app-assets');
const output = resolve(root, 'dist/mcp-app.html');
const expected = ['mcp-app.js', 'mcp-app.css', 'THIRD_PARTY_LICENSES.txt'];

try {
  await build({ configFile: resolve(root, 'vite.config.ts'), mode: 'mcp-app' });
  const files = await readdir(assets);
  if (files.length !== expected.length || expected.some((file) => !files.includes(file))) {
    throw new Error('MCP App build must produce exactly one JavaScript asset, one CSS asset, and one license report.');
  }
  const [javascript, css, licenses] = await Promise.all(expected.map((file) => readFile(resolve(assets, file), 'utf8')));
  const inlineScript = javascript.replace(/<\/script/gi, '<\\/script');
  const inlineLicenses = licenses.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  const footer = `<footer class="third-party-licenses"><details><summary>Third-party licenses</summary><pre>${inlineLicenses}</pre></details></footer>`;
  const html = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ANECHOIC Workbench</title><style>${css}</style><div id="app"></div>${footer}<script type="module">${inlineScript}</script></html>`;
  if (/<script\b[^>]*\bsrc=|<link\b[^>]*\brel=["']stylesheet/i.test(html)) throw new Error('MCP App must not reference external assets.');
  await writeFile(output, html);
} finally {
  await rm(assets, { recursive: true, force: true });
}
