
import { expect, test } from '@playwright/test';
import { replaceSql } from './workbench-fixture';
import { mockGraph } from './console-graph-mock';
import { toolReply, toolRequest } from './tool_rest_fixture';

test('browser fetches inline rows while MCP defaults to files',
  async ({ page }) => {
  const url = new URL(process.env.WORKBENCH_E2E_URL!);
  const fetched: Record<string, unknown>[] = [];
  page.on('request', request => {
    if (request.method() !== 'POST' ||
      !request.url().endsWith('/tools')) return;
    const input = request.postDataJSON();
    if (input?.name === 'view_fetch') fetched.push(input.arguments);
  });
  await page.goto(url.toString());
  await replaceSql(page, 'SELECT 42 AS inline_result');
  await page.getByRole('textbox', { name:
    'Query editor' }).press('Meta+Enter');
  await expect(page.getByRole('grid')).toBeVisible();
  await expect(page.getByRole('grid')).toContainText('inline_result');
  await expect(page.getByRole('grid')).toContainText('42');
  expect(fetched.length).toBeGreaterThan(0);
  expect(fetched.every(input =>
    input.result_delivery === 'inline')).toBe(true);
});

test('keeps the save refusal visible when the completed result is paged',
  async ({ page }) => {
  const saveError = 'Saved query storage is unavailable';
  await page.route('**/tools', async (route) => {
    const input = toolRequest(route);
    if (input?.name !== 'view_run' ||
      !input.arguments.save) return route.fallback();

    delete input.arguments.save;
    delete input.arguments.name;
    const response = await route.fetch({ postData: input });
    expect(response.ok()).toBe(true);
    const envelope = await response.json();
    const value = envelope.result.value;
    expect(value.status).toBe('success');
    envelope.result.value = { ...value, outcome: 'partial',
      save_error: saveError };
    await route.fulfill({ response, json: envelope });
  });

  await page.goto(process.env.WORKBENCH_E2E_URL!);
  const sql = 'SELECT i AS retained_value FROM range(220) AS t(i)';
  await replaceSql(page, sql);
  await expect(page.getByRole('textbox', {
    name: 'Query editor' })).toHaveText(sql);
  await page.getByRole('button', { name: 'Run & Save', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Bookmark name' });
  await dialog.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('grid')).toContainText('retained_value');
  const pages = page.getByRole('navigation', { name: 'Result pages' });
  await pages.getByRole('button', { name: 'Next' }).click();
  await expect(pages.getByRole('button', { name: 'Previous' })).toBeEnabled();
  await expect(page.getByRole('alert').filter(
    { hasText: saveError })).toBeVisible();
  await expect(page.getByRole('tab', { name:
    'View 1 *', exact: true })).toBeVisible();
  await expect(page.locator('.saved-reference')).toHaveCount(0);
});

for (const save of [false, true]) {
  for (const [reason, queryId] of [
    ['missing', undefined], ['blank', '   '], ['mismatched', 'run-1'],
  ] as const) {
    const hasResultId = reason === 'mismatched';
    const action = save ? 'Run & Save' : 'Run';
    test(`${action} rejects a ${reason} result ID`, async ({ page }) => {
      await mockGraph(page, 'table', 'vertical', 'SELECT 1');
      let submitted = false;
      let fetches = 0;
      let refreshed = false;
      await page.route('**/tools', async route => {
        if (route.request().method() !== 'POST') return route.fallback();
        const { name, arguments: args } = toolRequest(route);
        if (name === 'view_run') {
          expect(Boolean(args.save)).toBe(save);
          submitted = true;
          return route.fulfill({ json: toolReply(route, { status: 'success',
            revision: 1, query_id: queryId, save_error: 'Save refused' }) });
        }
        if (submitted && name === 'view_fetch') {
          fetches++;
          return route.fulfill({ json: toolReply(route, { query_id:
            'run-2', columns: [], rows: [] }) });
        }
        if (submitted && name === 'query_saved_list') refreshed = true;
        return route.fallback();
      });
      await page.goto(process.env.WORKBENCH_E2E_URL!);
      await expect(page.getByRole('grid')).toBeVisible();
      const run = page.getByRole('button', {
        name: save ? 'Run & Save' : /^Run Cmd/ });
      await run.click();
      if (save) await page.getByRole('dialog',
        { name: 'Bookmark name' }).getByRole(
        'button', { name: 'Save', exact: true }).click();
      await expect(page.getByRole('alert').filter({ hasText: hasResultId
        ? 'The View result changed before it could be displayed.' :
          'The completed query has no result ID.' })).toBeVisible();
      await expect(page.getByRole('alert').filter({
        hasText: 'Save refused' })).toBeVisible();
      await expect(run).toBeEnabled();
      await expect(page.getByRole('grid')).toHaveCount(0);
      if (save) await expect.poll(() => refreshed).toBe(true);
      else expect(refreshed).toBe(false);
      expect(fetches).toBe(hasResultId ? 1 : 0);
    });
  }
}
