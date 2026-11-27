import assert from 'node:assert/strict';
import test from 'node:test';
import { loadLib } from './FEATURE_IWE_CONSOLE_FRONTEND__tests__shared.ts';

const { HttpOperationCaller, McpAppTransport, lifecycleResult } = await loadLib();
const instance = 'a'.repeat(64);
const project = { prefix: 'AN', instance_id: instance };

test('HTTP sends Tool names and optional Project roots to the REST API',
  async () => {
  const previous = globalThis.fetch;
  try {
    for (const root of [null, '', '/Project A']) {
      const args = { sql: 'SELECT 1' };
      const value = { query_id: 'first' };
      globalThis.fetch = async (url, request) => {
        assert.equal(url, '/tools');
        assert.equal(request?.method, 'POST');
        const headers = new Headers(request?.headers);
        assert.equal(headers.get('content-type'), 'application/json');
        assert.equal(headers.get('X-Anechoic-Project-Instance'), instance);
        assert.deepEqual(JSON.parse(String(request?.body)), {
          name: 'new_tool',
          arguments: root ? { ...args, project_root: root } : args,
          session_id: null,
          public_base_url: null,
        });
        return Response.json({ result: { value, text: 'Tool text' }, project });
      };
      const caller = new HttpOperationCaller(instance, root);
      assert.deepEqual(await caller.call('new_tool', args), value);
    }
  } finally { globalThis.fetch = previous; }
});

test('HTTP preserves partial saves and lifecycle failures inside Tool results',
  async () => {
  const previous = globalThis.fetch;
  try {
    const caller = new HttpOperationCaller(instance, null);
    const partial = { outcome: 'partial', save_error: 'save failed' };
    globalThis.fetch = async () => Response.json({
      result: { value: partial, text: null }, project,
    });
    assert.deepEqual(await caller.call('query_run', {}), partial);
    const blocked = { status: 'blocked', errors: [{
      code: 'source_changed', message: 'The source changed.',
    }] };
    globalThis.fetch = async () => Response.json({
      result: { value: blocked, text: null }, project,
    });
    const value = await caller.call('atom_lifecycle_update', {});
    assert.deepEqual(value, blocked);
    assert.throws(() => lifecycleResult(value), {
      message: 'The source changed.', code: 'source_changed',
    });
  } finally { globalThis.fetch = previous; }
});

test('HTTP preserves Tool and Project faults at either HTTP status',
  async () => {
  const previous = globalThis.fetch;
  try {
    const caller = new HttpOperationCaller(instance, null);
    for (const status of [200, 400]) {
      globalThis.fetch = async () => Response.json({ error: {
        message: 'bad SQL', code: 'query_error', scope: 'tool',
        tool_result: { outcome: 'failed', diagnostics: ['query_error: bad SQL'] },
      }, project }, { status });
      await assert.rejects(caller.call('query_run', {}), {
        message: 'bad SQL', code: 'query_error',
      });
    }
    globalThis.fetch = async () => Response.json({ error: {
      message: 'Select a Project.', code: 'missing_project_root',
      scope: 'project',
    }, project: null });
    await assert.rejects(caller.call('query_run', {}), {
      message: 'Select a Project.', code: 'missing_project_root',
    });
  } finally { globalThis.fetch = previous; }
});

test('HTTP rejects malformed responses and missing or mismatched receipts',
  async () => {
  const previous = globalThis.fetch;
  try {
    const caller = new HttpOperationCaller(instance, null);
    globalThis.fetch = async () => assert.fail('Fetch without a Project instance');
    for (const invalid of [undefined, 'malformed']) {
      await assert.rejects(new HttpOperationCaller(invalid, null).call(
        'query_run', {}), /no valid Project instance/);
    }
    globalThis.fetch = async () => new Response(
      '<html>unavailable</html>', { status: 503 });
    await assert.rejects(caller.call('query_run', {}), /expected JSON/);
    globalThis.fetch = async () => new Response('[]');
    await assert.rejects(caller.call('query_run', {}), /expected an object/);
    globalThis.fetch = async () => Response.json({ error: 'bad SQL' });
    await assert.rejects(caller.call('query_run', {}), /error response/);
    globalThis.fetch = async () => Response.json({
      result: { value: {}, text: false }, project,
    });
    await assert.rejects(caller.call('query_run', {}), /expected a Tool result/);
    for (const receipt of [undefined, { ...project, instance_id: 'b'.repeat(
      64) }]) {
      globalThis.fetch = async () => Response.json({
        result: { value: {}, text: null }, project: receipt,
      });
      await assert.rejects(caller.call('query_run', {}), {
        code: 'project_receipt_mismatch',
      });
    }
  } finally { globalThis.fetch = previous; }
});

test('MCP preserves validated Tool diagnostics and codes', async () => {
  const previous = globalThis.window;
  let receive: (event: { source: object; data: unknown }) => void;
  let result: { isError: boolean;
    structuredContent: Record<string, unknown> } = {
    isError: true, structuredContent: { outcome:
      'failed', diagnostics: ['query_error: bad SQL'] },
  };
  const host = { postMessage(request: { id: number }) {
    receive({ source: host, data: { jsonrpc:
      '2.0', id: request.id, result } });
  } };
  globalThis.window = {
    parent: host, addEventListener: (_event: string,
      handler: typeof receive) => { receive = handler; },
  } as unknown as typeof window;
  try {
    const caller = new McpAppTransport(window.parent);
    caller['input'] = { sessionId: 'session', projectRoot: '/project' };
    await assert.rejects(caller.call('query_run', {}), {
      message: 'query_error: bad SQL', code: 'query_error' });
    result = { isError: true, structuredContent: {} };
    await assert.rejects(caller.call('query_run', {
      }), /Invalid Workbench tool error response/);
    result = { isError: false, structuredContent: {
      outcome: 'partial', save_error: 'save failed' } };
    assert.equal((await caller.call<{ save_error: string }>(
      'query_run', {})).save_error, 'save failed');
  } finally { globalThis.window = previous; }
});
