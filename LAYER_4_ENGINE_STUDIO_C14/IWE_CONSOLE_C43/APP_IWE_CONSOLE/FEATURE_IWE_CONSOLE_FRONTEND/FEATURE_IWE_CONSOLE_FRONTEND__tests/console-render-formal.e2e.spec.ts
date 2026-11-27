import { expect, test, type Page } from '@playwright/test';
import { checkObservedEffects, formalCases, type Effect,
  type EffectCase } from './console-formal-cases';
import { toolReply, toolRequest } from './tool_rest_fixture';

type RenderCase = EffectCase & { input: { transport: string; entry: string } };
const { render_console_view: cases } =
  formalCases<RenderCase>('render_console_view');
const refusal = 'Query refused by the Project.';

async function mockRun(page: Page, succeeds: boolean) {
  const view = { id: 'v1', name: 'Source', sql:
    'SELECT 1 AS value', cursor_position: 0, revision: 1 };
  const workspace = { project_name: 'Fixture', workspace_id:
    'test', active_view_id: view.id, views: [view] };
  const query = { query_id: 'query-render', revision: view.revision };
  await page.route('**/tools', async route => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'query_schema': value = { tables: {} }; break;
      case 'iwe_console_status': value = { mode: 'unavailable' }; break;
      case 'query_saved_list': case 'query_log_list': value = { items: [] }; break;
      case 'workspace_open':
      case 'workspace_get': value = workspace; break;
      case 'view_run': value = succeeds ? { ...query, status: 'success' } :
        { ...query, status: 'failed', error: refusal }; break;
      case 'view_fetch': value = {
        ...query, columns: [{ name: 'value', type:
          'INTEGER', has_values: true }], rows: [[1]],
        column_count: 1, row_count: 1, offset:
          0, page_size: 100, has_more: false,
      }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, value) });
  });
}

for (const scenario of cases) {
  test(`formal render: ${scenario.name}`, async ({ page }) => {
    expect(scenario.input.transport).toBe('in_process');
    expect(scenario.input.entry).toMatch(/\/src\/App\.svelte$/);
    expect(['failed', 'succeeded']).toContain(scenario.name);
    const succeeds = scenario.name === 'succeeded';
    await mockRun(page, succeeds);
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    const panel = page.locator('.results-panel');
    await panel.evaluate(panel => {
      panel.setAttribute('data-formal-displayed', 'false');
      const observer = new MutationObserver(() => {
        if (panel.querySelector('[role="grid"] .tabulator-cell')) {
          panel.setAttribute('data-formal-displayed', 'true');
          observer.disconnect();
        }
      });
      observer.observe(panel, { childList: true, subtree: true });
    });
    await page.getByRole('button', { name: /^Run Cmd/ }).click();
    if (succeeds) await expect(page.getByRole('grid').locator(
      '.tabulator-cell').first()).toHaveText('1');
    else await expect(page.getByRole('alert')).toHaveText(refusal);
    const displayed = await panel.getAttribute('data-formal-displayed');
    expect(displayed).not.toBeNull();
    const observed: Effect[] = displayed === 'true' ?
      [['C46.console', 'view_displayed']] : [];
    checkObservedEffects(scenario, observed);
  });
}

test(
  'effect checks reject an omitted, forbidden, or out-of-order observation',
    () => {
  const request: Effect = ['api', 'requested'];
  const receipt: Effect = ['api', 'succeeded'];
  const shown: Effect = ['view', 'displayed', { dirty: false }];
  const scenario: EffectCase = {
    name: 'render',
    must_effect: [request, receipt, shown],
    forbid_effect: ['stale_view'],
    must_precede: [[request, receipt], [receipt, shown]],
  };
  checkObservedEffects(scenario, [request, receipt, shown]);
  expect(() => checkObservedEffects(scenario, [
    receipt, shown])).toThrow(/missing effect/);
  expect(() => checkObservedEffects(scenario, [request, receipt, [
    'view', 'displayed', { dirty: true }]])).toThrow(/missing effect/);
  expect(() => checkObservedEffects(scenario, [request, receipt,
    shown, ['stale_view', 'displayed']])).toThrow(/forbidden effect/);
  expect(() => checkObservedEffects(scenario, [
    receipt, request, shown])).toThrow(/must precede/);
});
