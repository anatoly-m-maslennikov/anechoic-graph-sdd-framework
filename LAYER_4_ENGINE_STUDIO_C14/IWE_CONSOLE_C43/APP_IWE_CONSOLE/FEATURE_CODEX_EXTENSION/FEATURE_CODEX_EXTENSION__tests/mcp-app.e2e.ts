

import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const tests = dirname(fileURLToPath(import.meta.url));
const require = createRequire(new URL('../../FEATURE_IWE_CONSOLE_FRONTEND/package.json', import.meta.url));
const { chromium } = require('@playwright/test') as typeof import('../../FEATURE_IWE_CONSOLE_FRONTEND/node_modules/@playwright/test');
const ts = require('typescript') as typeof import('../../FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript');
type Outcome = 'fullscreen' | 'inline' | 'error' | 'unsupported';
declare global { interface Window { probeCalls: unknown[]; displayRequests: unknown[]; appModes: string[] } }

function probe(): string {
  const html = fs.readFileSync(resolve(tests, 'mcp_app_probe.html'), 'utf8');
  const source = fs.readFileSync(resolve(tests, 'mcp_app_probe.ts'), 'utf8');
  const script = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext } }).outputText;
  return html.replace('</html>', `<script type="module">${script}</script></html>`);
}

test('MCP App receives the initial result and calls a separate read-only tool', async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setContent('<iframe title="probe"></iframe>');
    await page.evaluate(html => {
      const frame = document.querySelector<HTMLIFrameElement>('iframe')!;
      window.probeCalls = [];
      window.addEventListener('message', event => {
        if (event.source !== frame.contentWindow || event.data?.jsonrpc !== '2.0') return;
        const { id, method, params } = event.data;
        if (id === undefined) return;
        const send = (message: object) => frame.contentWindow!.postMessage({ jsonrpc: '2.0', ...message }, '*');
        if (method === 'ui/initialize') {
          send({ id, result: { protocolVersion: '2026-01-26', hostInfo: { name: 'test-host', version: '1' }, hostCapabilities: {} } });
          send({ method: 'ui/notifications/tool-input', params: { arguments: { project_root: '/trusted/project' } } });
          send({ method: 'ui/notifications/tool-result', params: { structuredContent: { message: 'Initial host result' } } });
        } else if (method === 'tools/call') {
          window.probeCalls.push(params);
          send({ id, result: { isError: false, structuredContent: { message: 'Tool bridge passed' } } });
        }
      });
      frame.srcdoc = html;
    }, probe());
    const frame = page.frameLocator('iframe');
    await frame.getByText('Host bridge connected', { exact: true }).waitFor();
    await frame.getByText('Initial host result', { exact: true }).waitFor();
    await frame.getByRole('button', { name: 'Test tool bridge' }).click();
    await frame.getByText('Tool bridge passed', { exact: true }).waitFor();
    assert.deepEqual(await page.evaluate(() => window.probeCalls), [{
      name: 'workbench_ui_ping', arguments: { project_root: '/trusted/project' },
    }]);
    assert.deepEqual(errors, []);
  } finally {
    await browser.close();
  }
});

async function connectPresentationHost(page: import('../../FEATURE_IWE_CONSOLE_FRONTEND/node_modules/@playwright/test').Page, outcome: Outcome) {
  await page.setContent('<iframe title="probe"></iframe>');
  await page.evaluate(({ html, outcome }) => {
    const frame = document.querySelector<HTMLIFrameElement>('iframe')!;
    window.displayRequests = [];
    window.addEventListener('message', event => {
      if (event.source !== frame.contentWindow || event.data?.jsonrpc !== '2.0') return;
      const { id, method, params } = event.data;
      const send = (message: object) => frame.contentWindow!.postMessage({ jsonrpc: '2.0', ...message }, '*');
      if (method === 'ui/initialize') {
        window.appModes = params.appCapabilities.availableDisplayModes;
        send({ id, result: { hostContext: {
          displayMode: 'inline',
          availableDisplayModes: outcome === 'unsupported' ? ['inline'] : ['inline', 'fullscreen'],
        } } });
      } else if (method === 'ui/request-display-mode') {
        window.displayRequests.push(params);
        send(outcome === 'error'
          ? { id, error: { code: -32601, message: 'Expansion not supported' } }
          : { id, result: { mode: outcome === 'inline' ? 'inline' : 'fullscreen' } });
      }
    });
    frame.srcdoc = html;
  }, { html: probe(), outcome });
}

test('presentation uses offered modes and reports the actual host response', async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const outcome of ['fullscreen', 'inline', 'error', 'unsupported'] as const) {
      const page = await browser.newPage();
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await connectPresentationHost(page, outcome);
      const frame = page.frameLocator('iframe');
      await frame.getByText('Host bridge connected', { exact: true }).waitFor();
      assert.deepEqual(await page.evaluate(() => window.appModes), ['inline', 'fullscreen']);
      const expand = frame.getByRole('button', { name: 'Expand', exact: true });
      assert.equal(await expand.isEnabled(), outcome !== 'unsupported');
      if (outcome === 'unsupported') {
        assert.deepEqual(await page.evaluate(() => window.displayRequests), []);
        await page.evaluate(() => document.querySelector<HTMLIFrameElement>('iframe')!.contentWindow!.postMessage({
          jsonrpc: '2.0', method: 'ui/notifications/host-context-changed',
          params: { availableDisplayModes: ['inline', 'fullscreen'] },
        }, '*'));
      }
      await expand.click();
      await page.waitForFunction(() => window.displayRequests.length === 1);
      if (outcome === 'inline' || outcome === 'error') {
        await page.waitForFunction(() => !document.querySelector<HTMLIFrameElement>('iframe')!.contentDocument!.querySelector<HTMLButtonElement>('#expand')!.disabled);
      }
      const expected = outcome === 'error' ? 'Expansion failed: Expansion not supported'
        : `Presentation: ${outcome === 'inline' ? 'inline' : 'fullscreen'}; available: inline, fullscreen`;
      await frame.getByText(expected, { exact: true }).waitFor();
      if (outcome === 'error') {
        await frame.getByText('Presentation: inline; available: inline, fullscreen', { exact: true }).waitFor();
      }
      assert.deepEqual(await page.evaluate(() => window.displayRequests), [{ mode: 'fullscreen' }]);
      assert.deepEqual(errors, []);
      await page.close();
    }
  } finally {
    await browser.close();
  }
});
