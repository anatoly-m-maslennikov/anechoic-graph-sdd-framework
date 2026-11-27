import { mockGraph } from './console-graph-mock';
import { checkObservedValues, formalCases, type CorrelatedCase } from './console-formal-cases';
import { expect, test, type Page } from '@playwright/test';

type Case = CorrelatedCase & { input: Record<string, string>; effect: [string, string, Record<string, string>] };
const cases = formalCases<Case>('edit_console_builder', 'run_console_builder', 'select_console_view', 'inspect_console_diagnostics');

async function builderFixture(page: Page, fault?: 'revision' | 'query_id') {
  const operations: { operation: string; arguments: any; reply: any }[] = [];
  const view = { id: 'v1', name: 'View 1', sql: 'SELECT * FROM atoms LIMIT 5', cursor_position: 0, revision: 1 };
  const workspace = { workspace_id: 'test', project_name: 'Fixture', active_view_id: view.id, views: [view] };
  let run = { view_id: '', revision: 0, query_id: '', sql: '' };
  await page.route('**/*', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    const path = new URL(route.request().url()).pathname;
    if (!path.endsWith('/interface')) return route.fulfill({ json: path.endsWith('/schema') ? { tables: {} } : { items: [] } });
    const request = route.request().postDataJSON();
    let reply: unknown = { items: [] };
    switch (request.operation) {
      case 'workspace_open': case 'workspace_get': reply = workspace; break;
      case 'view_update':
        view.sql = request.arguments.sql; view.revision++; reply = { ...view }; break;
      case 'view_run':
        run = { view_id: request.arguments.view_id, revision: view.revision, query_id: `query-${view.revision}`, sql: view.sql };
        reply = { status: 'success', ...run, revision: fault === 'revision' ? run.revision - 1 : run.revision }; break;
      case 'view_fetch':
        reply = { query_id: fault === 'query_id' ? 'stale-query' : run.query_id,
          columns: ['view_id', 'revision', 'query_id', 'sql'].map(name => ({ name, type: 'VARCHAR', has_values: true })),
          rows: [[run.view_id, run.revision, run.query_id, run.sql]], row_count: 1, column_count: 4,
          offset: 0, page_size: request.arguments.page_size, has_more: false }; break;
    }
    if (['view_update', 'view_run', 'view_fetch'].includes(request.operation)) operations.push({ ...request, reply });
    return route.fulfill({ json: reply });
  });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await expect(page.getByRole('textbox', { name: 'Query editor' })).toHaveText(view.sql);
  return { view, operations };
}

for (const scenario of cases.run_console_builder) {
  test(`formal Builder Run: ${scenario.name}`, async ({ page }) => {
    const { view, operations } = await builderFixture(page);
    const builder = page.getByLabel('SQL builder');
    const editor = page.getByRole('textbox', { name: 'Query editor' });
    const cells = page.getByRole('grid').locator('.tabulator-cell');
    for (const [field, value, fragment] of [
      ['Component', 'C01', `"header.container.component" = 'C01'`],
      ['Tier', '2', '"header.tier" = 2'],
      ['Template', 'solution', `"header.context.template" = 'solution'`],
      ['Limit', '3', 'LIMIT 3'],
    ]) {
      const start = operations.length;
      const base = view.revision;
      await builder.getByLabel(field).fill(value); await builder.getByLabel(field).blur();
      await expect(editor).toContainText(fragment);
      await expect(cells.nth(2)).toHaveText(`query-${base + 1}`);
      const [update, run, fetch] = operations.slice(start)
        .filter(call => call.operation !== 'view_fetch' || call.reply.query_id === `query-${base + 1}`);
      expect([update.operation, run.operation, fetch.operation]).toEqual(['view_update', 'view_run', 'view_fetch']);
      const [viewId, revision, queryId, sql] = await cells.allTextContents();
      checkObservedValues(scenario, {
        edited_run: { view_id: view.id, sql: await editor.innerText(), revision: base },
        update_requested: update.arguments, update_returned: update.reply,
        run_requested: run.arguments, run_returned: run.reply,
        fetch_requested: fetch.arguments, first_page_received: fetch.reply,
        result_displayed: { view_id: viewId, revision: Number(revision), query_id: queryId, sql },
      });
    }
    const submitted = operations.filter(item => item.operation === 'view_run').length;
    await builder.getByLabel('Limit').fill('bad'); await builder.getByLabel('Limit').blur();
    await expect(page.getByRole('alert')).toHaveText('Limit must be a non-negative integer.');
    await expect(editor).toContainText('LIMIT 3');
    expect(operations.filter(item => item.operation === 'view_run')).toHaveLength(submitted);
  });

  for (const fault of ['revision', 'query_id'] as const) {
    test(`formal Builder Run: ${scenario.name} refuses stale ${fault}`, async ({ page }) => {
      const { operations } = await builderFixture(page, fault);
      const limit = page.getByLabel('SQL builder').getByLabel('Limit');
      await limit.fill('3'); await limit.blur();
      const error = fault === 'revision' ? 'The View changed before its query could be displayed.'
        : 'The View result changed before it could be displayed.';
      await expect(page.getByRole('alert')).toHaveText(error);
      await expect(page.getByRole('grid')).toHaveCount(0);
      expect(operations.map(item => item.operation)).toEqual(fault === 'revision'
        ? ['view_update', 'view_run'] : ['view_update', 'view_run', 'view_fetch']);
    });
  }
}

test('diagnostics displays health and reports both rebuild outcomes', async ({ page }) => {
  const targets: string[] = [];
  const statusRequests: Record<string, unknown>[] = [];
  let unhealthy = false;
  const workspace = { workspace_id: 'test', project_name: 'Fixture', active_view_id: 'v1', views: [{ id: 'v1', name: 'View 1', sql: 'SELECT 1', cursor_position: 0, revision: 1 }] };
  await page.route('**/*', async (route) => {
    if (route.request().method() !== 'POST') return route.continue();
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith('/status')) {
      statusRequests.push(route.request().postDataJSON());
      return route.fulfill({ json: unhealthy
      ? { mode: 'unavailable', health: { state: 'degraded' }, last_synced_at: null, archive: { state: 'failed' }, ingestion_issues: [{ atom_ref: 'AN-S-1', message: 'Bad source' }] }
      : { mode: 'live_index', health: { state: 'ready' }, last_synced_at: '2026-01-01T00:00:00Z', archive: { state: 'ready' }, ingestion_issues: [] } });
    }
    if (path.endsWith('/rebuild')) {
      const { target } = route.request().postDataJSON(); targets.push(target);
      if (target === 'all') return route.fulfill({ status: 409, json: { error: 'Rebuild refused by fixture' } });
      unhealthy = true; return route.fulfill({ json: { outcome: 'completed' } });
    }
    if (path.endsWith('/interface')) {
      const { operation } = route.request().postDataJSON();
      return route.fulfill({ json: operation === 'workspace_open' || operation === 'workspace_get' ? workspace : { items: [] } });
    }
    return route.fulfill({ json: path.endsWith('/schema') ? { tables: [] } : { items: [] } });
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

async function mockOperations(page: import('@playwright/test').Page, input: Case['input']) {
  const { health_state: health = 'ready', target, reply, issue, ref } = input;
  let failedBuild = false;
  const view = { id: 'v1', name: 'View 1', sql: input.sql ?? 'SELECT 1', cursor_position: 0, revision: 1 };
  await page.route('**/*', async (route) => {
    if (route.request().method() !== 'POST') return route.continue();
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith('/status')) {
      const message = failedBuild ? input.failure_issue : issue;
      return route.fulfill({ json: {
        mode: 'live_index', health: { state: health },
        last_run_state: failedBuild ? 'failed' : null,
        ingestion_issues: message ? [{ atom_ref: ref, message }] : [],
      } });
    }
    if (path.endsWith('/rebuild')) {
      expect(route.request().postDataJSON().target).toBe(target);
      failedBuild = reply === 'refused';
      return reply === 'refused' ? route.fulfill({ status: 409, json: { error: 'Rebuild refused by fixture' } })
        : route.fulfill({ json: { status: 'ready', target, result_ids: {} } });
    }
    if (path.endsWith('/interface')) {
      const { operation, arguments: args } = route.request().postDataJSON();
      if (operation === 'view_update') { view.sql = args.sql; view.revision++; return route.fulfill({ json: view }); }
      const workspace = { workspace_id: 'test', project_name: 'Fixture', active_view_id: 'v1', views: [view] };
      return route.fulfill({ json: operation === 'workspace_open' || operation === 'workspace_get' ? workspace : { items: [] } });
    }
    return route.fulfill({ json: path.endsWith('/schema') ? { tables: {} } : { items: [] } });
  });
}

for (const { name, input, effect } of cases.edit_console_builder) {
  test(`formal builder: ${name}`, async ({ page }) => {
    await builderFixture(page);
    const field = page.getByLabel('SQL builder').getByLabel(input.field);
    await expect(page.getByRole('textbox', { name: 'Query editor' })).toHaveText(input.sql);
    await field.fill(input.value); await field.blur();
    await expect(page.getByRole('textbox', { name: 'Query editor' })).toHaveText(effect[2].sql);
    if (effect[2].error) await expect(page.getByRole('alert')).toHaveText(effect[2].error);
  });
}

for (const { name, input, effect } of cases.select_console_view) {
  test(`formal View: ${name}`, async ({ page }) => {
    const { kind, layout, error } = effect[2];
    await mockGraph(page, kind, layout, input.sql, undefined, input.other_ref);
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    await expect(page.getByRole('combobox', { name: 'View', exact: true })).toHaveValue(kind);
    if (error) {
      await expect(page.getByRole('alert')).toHaveText(error);
      await expect(page.locator('.document-stack')).toHaveCount(0);
      await expect(page.getByRole('region', { name: 'Atom Graph' })).toHaveCount(0);
    } else if (kind === 'table') await expect(page.getByRole('grid')).toBeVisible();
    else if (kind === 'document') await expect(page.locator('.document-stack')).toBeVisible();
    else if (kind === 'structure') await expect(page.getByText('Component One', { exact: true })).toBeVisible();
    else await expect(page.getByRole('region', { name: kind === 'graph' ? 'Atom Graph' : 'Imports Graph' }))
      .toHaveAttribute('data-layout', layout);
  });
}

for (const { name, input, effect } of cases.inspect_console_diagnostics) {
  test(`formal Diagnostics: ${name}`, async ({ page }) => {
    await mockOperations(page, input);
    // Check the action's status refresh without help from the Workspace poll.
    if (input.reply === 'refused') await page.addInitScript(() => { (window as Window).setInterval = () => 0; });
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    await page.getByRole('tab', { name: 'Diagnostics' }).click();
    const panel = page.getByRole('region', { name: 'Diagnostics' });
    if (effect[2].runtime) await expect(panel).toContainText(effect[2].runtime);
    if (input.target) {
      await panel.getByRole('button', { name: input.target === 'all' ? 'Rebuild Project database from source' : 'Rebuild Realization Graph' }).click();
      if (effect[2].error) await expect(panel.getByRole('alert')).toHaveText(effect[2].error);
      else await expect(panel.getByRole('status')).toHaveText(effect[2].message);
    }
    if (effect[2].worker) await expect(panel.getByText(effect[2].worker, { exact: true })).toBeVisible();
    if (effect[2].issue) {
      await panel.getByText('Ingestion issues', { exact: true }).last().click();
      await expect(panel).toContainText(effect[2].issue);
      await expect(panel.getByRole('button', { name: effect[2].ref })).toBeVisible();
    }
  });
}
