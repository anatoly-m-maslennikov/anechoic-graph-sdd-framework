import assert from 'node:assert/strict';
import test from 'node:test';
import { loadLib } from './FEATURE_WORKBENCH_FRONTEND__tests__shared.ts';

const { HttpOperationCaller, McpAppTransport } = await loadLib();

test('HTTP preserves a public Tool refusal and rejects malformed responses', async () => {
  const previous = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response(JSON.stringify({ error: 'bad SQL', code: 'query_error',
      tool_result: { outcome: 'failed', diagnostics: ['query_error: bad SQL'] } }), { status: 400 });
    const caller = new HttpOperationCaller('/anechoic/workbench/p', null);
    await assert.rejects(caller.call('query_run', {}), { message: 'bad SQL', code: 'query_error' });
    globalThis.fetch = async () => new Response('<html>unavailable</html>', { status: 503 });
    await assert.rejects(caller.call('query_run', {}), /expected JSON/);
    globalThis.fetch = async () => new Response('[]');
    await assert.rejects(caller.call('query_run', {}), /expected an object/);
  } finally { globalThis.fetch = previous; }
});

test('MCP preserves validated Tool diagnostics and codes', async () => {
  const previous = globalThis.window;
  let receive: (event: { source: object; data: unknown }) => void;
  let result: { isError: boolean; structuredContent: Record<string, unknown> } = {
    isError: true, structuredContent: { outcome: 'failed', diagnostics: ['query_error: bad SQL'] },
  };
  const host = { postMessage(request: { id: number }) {
    receive({ source: host, data: { jsonrpc: '2.0', id: request.id, result } });
  } };
  globalThis.window = {
    parent: host, addEventListener: (_event: string, handler: typeof receive) => { receive = handler; },
  } as unknown as typeof window;
  try {
    const caller = new McpAppTransport(window.parent);
    caller['input'] = { sessionId: 'session', projectRoot: '/project' };
    await assert.rejects(caller.call('query_run', {}), { message: 'query_error: bad SQL', code: 'query_error' });
    result = { isError: true, structuredContent: {} };
    await assert.rejects(caller.call('query_run', {}), /Invalid Workbench tool error response/);
    result = { isError: false, structuredContent: { outcome: 'partial', save_error: 'save failed' } };
    assert.equal((await caller.call<{ save_error: string }>('query_run', {})).save_error, 'save failed');
  } finally { globalThis.window = previous; }
});
