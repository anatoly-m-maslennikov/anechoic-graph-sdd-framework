import { mockGraph } from './console-graph-mock';
import { checkObservedEffects, checkObservedValues, formalCases,
  type CorrelatedCase, type Effect } from './console-formal-cases';
import { expect, test, type Page, type Request, type Route } from '@playwright/test';
import { toolReply, toolRequest } from './tool_rest_fixture';

type Case = CorrelatedCase & { input: Record<string, string>;
  effect: [string, string, Record<string, string>] };
const cases = formalCases<Case>('edit_console_builder', 'run_console_builder',
  'select_console_view', 'inspect_console_diagnostics');

const builderEvents = {
  view_update: ['update_requested', 'update_returned', 'C21.view_update', 'succeeded'],
  view_run: ['run_requested', 'run_returned', 'C21.view_run.query_id', 'returned'],
  view_fetch: ['fetch_requested', 'first_page_received', 'C21.view_fetch', 'succeeded'],
} as const;
type BuilderObservation =
  | { phase: 'request' | 'response'; request:
    Request; operation: keyof typeof builderEvents }
  | { phase: 'display'; detail: Record<string, unknown> };

function observeBuilderDisplay() {
  const report = (window as typeof window & { reportBuilderDisplay(
    detail: Record<string, unknown>): Promise<void> })
    .reportBuilderDisplay;
  const seen = new Set<string>();
  new MutationObserver(() => {
    const cells = Array.from(document.querySelectorAll('[role="grid"] .tabulator-cell'));
    if (cells.length !== 4 || !cells[2].checkVisibility()) return;
    const [viewId, revision, queryId, sql] = cells.map(cell => cell.textContent ?? '');
    if (!viewId || !revision || !queryId || !sql || seen.has(queryId)) return;
    seen.add(queryId);
    void report({ view_id: viewId, revision: Number(revision), query_id: queryId, sql });
  }).observe(document, { childList: true, characterData:
    true, subtree: true, attributes: true });
}

async function observeBuilder(page: Page) {
  const observations: BuilderObservation[] = [];
  function record(request: Request, phase: 'request' | 'response') {
    if (request.method() !== 'POST' || !new URL(request.url(
      )).pathname.endsWith('/tools')) return;
    const { name: operation } = request.postDataJSON();
    if (Object.hasOwn(builderEvents,
      operation)) observations.push({ request, operation, phase });
  }
  page.on('request', request => record(request, 'request'));
  page.on('requestfinished', request => record(request, 'response'));
  await page.exposeFunction('reportBuilderDisplay', (detail: Record<string, unknown>) => {
    observations.push({ phase: 'display', detail });
  });
  await page.addInitScript(observeBuilderDisplay);
  return observations;
}

async function builderEffect(observation:
  BuilderObservation): Promise<[string, Effect] | undefined> {
  if (observation.phase === 'display') return ['result_displayed',
    ['workbench_display', 'shown', observation.detail]];
  const { request, operation, phase } = observation;
  const [requested, returned, target, outcome] = builderEvents[operation];
  if (phase === 'request') return [requested, [`C21.${operation}`,
    'requested', request.postDataJSON().arguments]];
  const response = await request.response();
  if (!response?.ok()) return;
  const { result } = await response.json();
  const detail = result?.value;
  if (!detail || operation === 'view_run' && (typeof detail.query_id !== 'string' ||
    !detail.query_id.trim())) return;
  return [returned, [target, outcome, detail]];
}

async function builderFixture(page: Page, fault?: 'revision' | 'query_id') {
  const observations = await observeBuilder(page);
  const view = { id: 'v1', name: 'View 1', sql:
    'SELECT * FROM atoms LIMIT 5', cursor_position: 0, revision: 1 };
  const workspace = { workspace_id: 'test', project_name:
    'Fixture', active_view_id: view.id, views: [view] };
  let run = { view_id: '', revision: 0, query_id: '', sql: '' };
  await page.route('**/tools', async route => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let reply: unknown;
    switch (name) {
      case 'query_schema': reply = { tables: {} }; break;
      case 'iwe_console_status': reply = { mode: 'unavailable' }; break;
      case 'query_saved_list': case 'query_log_list': reply = { items: [] }; break;
      case 'workspace_open': case 'workspace_get': reply = workspace; break;
      case 'view_update':
        view.sql = args.sql as string; view.revision++; reply = { ...view }; break;
      case 'view_run':
        run = { view_id: args.view_id as string, revision: view.revision,
          query_id: `query-${view.revision}`, sql: view.sql };
        reply = { status: 'success', ...run, revision:
          fault === 'revision' ? run.revision - 1 : run.revision }; break;
      case 'view_fetch':
        reply = { query_id: fault === 'query_id' ? 'stale-query' : run.query_id,
          columns: ['view_id', 'revision', 'query_id', 'sql'].map(
            name => ({ name, type: 'VARCHAR', has_values: true })),
          rows: [[run.view_id, run.revision, run.query_id,
            run.sql]], row_count: 1, column_count: 4,
          offset: 0, page_size: args.page_size, has_more: false }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, reply) });
  });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await expect(page.getByRole('textbox', { name: 'Query editor' })).toHaveText(view.sql);
  return { view, observations };
}

for (const scenario of cases.run_console_builder) {
  test(`formal Builder Run: ${scenario.name}`, async ({ page }) => {
    const { view, observations } = await builderFixture(page);
    const builder = page.getByLabel('SQL builder');
    const editor = page.getByRole('textbox', { name: 'Query editor' });
    const cells = page.getByRole('grid').locator('.tabulator-cell');
    for (const [field, value, fragment] of [
      ['Component', 'C01', `"header.container.component" = 'C01'`],
      ['Tier', '2', '"header.tier" = 2'],
      ['Template', 'solution', `"header.context.template" = 'solution'`],
      ['Limit', '3', 'LIMIT 3'],
    ]) {
      const start = observations.length;
      const base = view.revision;
      await builder.getByLabel(field).fill(value); await builder.getByLabel(field).blur();
      await expect(editor).toContainText(fragment);
      const queryId = `query-${base + 1}`;
      await expect(cells.nth(2)).toHaveText(queryId);
      await expect.poll(() => observations.some(entry =>
        entry.phase === 'display' && entry.detail.query_id === queryId)).toBe(true);
      const effects = (await Promise.all(observations.slice(start).map(
        builderEffect))).filter(effect => effect !== undefined);
      checkObservedEffects(scenario, effects.map(([, effect]) => effect));
      const values: Record<string, Record<string, unknown>> = {};
      for (const [name, [, , detail]] of effects) values[name] ??= detail ?? {};
      checkObservedValues(scenario, {
        edited_run: { view_id: view.id, sql: await editor.innerText(), revision: base },
        ...values,
      });
    }
    const submitted = observations.filter(item =>
      item.phase === 'request' && item.operation === 'view_run').length;
    await builder.getByLabel('Limit').fill('bad');
      await builder.getByLabel('Limit').blur();
    await expect(page.getByRole('alert')).toHaveText(
      'Limit must be a non-negative integer.');
    await expect(editor).toContainText('LIMIT 3');
    expect(observations.filter(item => item.phase === 'request' &&
      item.operation === 'view_run')).toHaveLength(submitted);
  });

  for (const fault of ['revision', 'query_id'] as const) {
    test(`formal Builder Run: ${scenario.name} refuses stale ${fault}`,
      async ({ page }) => {
      const { observations } = await builderFixture(page, fault);
      const limit = page.getByLabel('SQL builder').getByLabel('Limit');
      await limit.fill('3'); await limit.blur();
      const error = fault === 'revision' ?
        'The View changed before its query could be displayed.'
        : 'The View result changed before it could be displayed.';
      await expect(page.getByRole('alert')).toHaveText(error);
      await expect(page.getByRole('grid')).toHaveCount(0);
      expect(observations.some(item => item.phase === 'display')).toBe(false);
      expect(observations.flatMap(item => item.phase === 'request' ?
        [item.operation] : [])).toEqual(fault === 'revision'
        ? ['view_update', 'view_run'] : ['view_update', 'view_run', 'view_fetch']);
    });
  }
}

function refuseRebuild(route: Route) {
  const message = 'Rebuild refused by fixture';
  return route.fulfill({ json: {
    error: { code: 'rebuild_failed', message, scope: 'tool',
      tool_result: { outcome: 'failed', diagnostics: [`rebuild_failed: ${message}`] } },
    project: toolReply(route, null).project,
  } });
}

test('diagnostics displays health and reports both rebuild outcomes', async ({ page }) => {
  const targets: string[] = [];
  const statusRequests: Record<string, unknown>[] = [];
  let unhealthy = false;
  const workspace = { workspace_id: 'test', project_name: 'Fixture', active_view_id: 'v1', views: [{ id: 'v1', name: 'View 1', sql: 'SELECT 1', cursor_position: 0, revision: 1 }] };
  await page.route('**/tools', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'iwe_console_status':
        statusRequests.push(args);
        value = unhealthy
          ? { mode: 'unavailable', health: { state: 'degraded' }, last_synced_at: null, archive: { state: 'failed' }, ingestion_issues: [{ atom_ref: 'AN-S-1', message: 'Bad source' }] }
          : { mode: 'live_index', health: { state: 'ready' }, last_synced_at: '2026-01-01T00:00:00Z', archive: { state: 'ready' }, ingestion_issues: [] };
        break;
      case 'query_rebuild':
        targets.push(args.target as string);
        if (args.target === 'all') return refuseRebuild(route);
        unhealthy = true; value = { outcome: 'completed' }; break;
      case 'workspace_open': case 'workspace_get': value = workspace; break;
      case 'query_schema': value = { tables: [] }; break;
      case 'query_saved_list': case 'query_log_list': value = { items: [] }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, value) });
  });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('tab', { name: 'Diagnostics' }).click();
  const panel = page.getByRole('region', { name: 'Diagnostics' });
  await expect(panel).toContainText('Available');
  await expect(panel).toContainText('Healthy');
  expect(statusRequests).toContainEqual({ include_health: true });
  await expect(panel).toContainText('2026-01-01T00:00:00Z');
  await expect(panel).toContainText('ready');
  await panel.getByRole('button', { name: 'Rebuild Realization Graph' }).click();
  await expect(panel.getByRole('status')).toHaveText('Realization Graph rebuild complete.');
  await expect(panel).toContainText('Unavailable');
  await expect(panel).toContainText('Unhealthy');
  await expect(panel).toContainText('failed');
  await panel.getByText('Ingestion issues', { exact: true }).last().click();
  await expect(panel).toContainText('Bad source');
  await expect(panel.getByRole('button', { name: 'AN-S-1' })).toBeVisible();
  await panel.getByRole('button', { name: 'Rebuild Project database from source' }).click();
  await expect(panel.getByRole('alert')).toHaveText('Rebuild refused by fixture');
  expect(targets).toEqual(['realization_graph', 'all']);
});

async function mockOperations(page: import(
  '@playwright/test').Page, input: Case['input']) {
  const { health_state: health = 'ready', target, reply, issue, ref } = input;
  let failedBuild = false;
  const view = { id: 'v1', name: 'View 1', sql:
    input.sql ?? 'SELECT 1', cursor_position: 0, revision: 1 };
  const workspace = { workspace_id: 'test', project_name:
    'Fixture', active_view_id: 'v1', views: [view] };
  await page.route('**/tools', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'iwe_console_status': {
        const message = failedBuild ? input.failure_issue : issue;
        value = {
          mode: 'live_index', health: { state: health },
          last_run_state: failedBuild ? 'failed' : null,
          ingestion_issues: message ? [{ atom_ref: ref, message }] : [],
        };
        break;
      }
      case 'query_rebuild':
        expect(args.target).toBe(target);
        failedBuild = reply === 'refused';
        if (failedBuild) return refuseRebuild(route);
        value = { status: 'ready', target, result_ids: {} }; break;
      case 'view_update':
        view.sql = args.sql as string; view.revision++; value = view; break;
      case 'workspace_open': case 'workspace_get': value = workspace; break;
      case 'query_schema': value = { tables: {} }; break;
      case 'query_saved_list': case 'query_log_list': value = { items: [] }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, value) });
  });
}

for (const { name, input, effect } of cases.edit_console_builder) {
  test(`formal builder: ${name}`, async ({ page }) => {
    await builderFixture(page);
    const field = page.getByLabel('SQL builder').getByLabel(input.field);
    await expect(page.getByRole('textbox', { name:
      'Query editor' })).toHaveText(input.sql);
    await field.fill(input.value); await field.blur();
    await expect(page.getByRole('textbox', { name:
      'Query editor' })).toHaveText(effect[2].sql);
    if (effect[2].error) await expect(page.getByRole(
      'alert')).toHaveText(effect[2].error);
  });
}

for (const { name, input, effect } of cases.select_console_view) {
  test(`formal View: ${name}`, async ({ page }) => {
    const { kind, layout, error } = effect[2];
    await mockGraph(page, kind, layout, input.sql, undefined, input.other_ref);
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    await expect(page.getByRole('combobox', { name:
      'View', exact: true })).toHaveValue(kind);
    if (error) {
      await expect(page.getByRole('alert')).toHaveText(error);
      await expect(page.locator('.document-stack')).toHaveCount(0);
      await expect(page.getByRole('region', { name: 'Atom Graph' })).toHaveCount(0);
    } else if (kind === 'table') await expect(page.getByRole('grid')).toBeVisible();
    else if (kind === 'document') await expect(
      page.locator('.document-stack')).toBeVisible();
    else if (kind === 'structure') await expect(page.getByText(
      'Component One', { exact: true })).toBeVisible();
    else await expect(page.getByRole('region', { name:
      kind === 'graph' ? 'Atom Graph' : 'Imports Graph' }))
      .toHaveAttribute('data-layout', layout);
  });
}

for (const { name, input, effect } of cases.inspect_console_diagnostics) {
  test(`formal Diagnostics: ${name}`, async ({ page }) => {
    await mockOperations(page, input);
    if (input.reply === 'refused') await page.addInitScript(
      () => { (window as Window).setInterval = () => 0; });
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    await page.getByRole('tab', { name: 'Diagnostics' }).click();
    const panel = page.getByRole('region', { name: 'Diagnostics' });
    if (effect[2].runtime) await expect(panel).toContainText(effect[2].runtime);
    if (input.target) {
      await panel.getByRole('button', { name: input.target === 'all' ?
        'Rebuild Project database from source' : 'Rebuild Realization Graph' }).click();
      if (effect[2].error) await expect(panel.getByRole(
        'alert')).toHaveText(effect[2].error);
      else await expect(panel.getByRole('status')).toHaveText(effect[2].message);
    }
    if (effect[2].worker) await expect(panel.getByText(
      effect[2].worker, { exact: true })).toBeVisible();
    if (effect[2].issue) {
      await panel.getByText('Ingestion issues', { exact: true }).last().click();
      await expect(panel).toContainText(effect[2].issue);
      await expect(panel.getByRole('button', { name: effect[2].ref })).toBeVisible();
    }
  });
}
