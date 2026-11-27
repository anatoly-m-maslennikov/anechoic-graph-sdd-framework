
import { expect, test } from '@playwright/test';
import { replaceSql } from './workbench-fixture';
import { mockGraph } from './console-graph-mock';

test('browser fetches inline rows while MCP defaults to files', async ({ page }) => {
  const url = new URL(process.env.WORKBENCH_E2E_URL!);
  const fetched: Record<string, unknown>[] = [];
  page.on('request', request => {
    if (request.method() !== 'POST' || !request.url().endsWith('/interface')) return;
    const input = request.postDataJSON();
    if (input?.operation === 'view_fetch') fetched.push(input.arguments);
  });
  await page.goto(url.toString());
  await replaceSql(page, 'SELECT 42 AS inline_result');
  await page.getByRole('textbox', { name: 'Query editor' }).press('Meta+Enter');
  await expect(page.getByRole('grid')).toBeVisible();
  await expect(page.getByRole('grid')).toContainText('inline_result');
  await expect(page.getByRole('grid')).toContainText('42');
  expect(fetched.length).toBeGreaterThan(0);
  expect(fetched.every(input => input.result_delivery === 'inline')).toBe(true);
});

test('keeps the save refusal visible when the completed result is paged', async ({ page }) => {
  const saveError = 'Saved query storage is unavailable';
  await page.route('**/interface', async (route) => {
    const input = route.request().postDataJSON();
    if (input.operation !== 'view_run' || !input.arguments.save) return route.continue();

    delete input.arguments.save;
    delete input.arguments.name;
    const response = await route.fetch({ postData: input });
    expect(response.ok()).toBe(true);
    const result = await response.json();
    expect(result.status).toBe('success');
    await route.fulfill({ response, json: { ...result, outcome: 'partial', save_error: saveError } });
  });

  await page.goto(process.env.WORKBENCH_E2E_URL!);
  const sql = 'SELECT i AS retained_value FROM range(220) AS t(i)';
  await replaceSql(page, sql);
  await expect(page.getByRole('textbox', { name: 'Query editor' })).toHaveText(sql);
  await page.getByRole('button', { name: 'Run & Save', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Bookmark name' });
  await dialog.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('grid')).toContainText('retained_value');
  const pages = page.getByRole('navigation', { name: 'Result pages' });
  await pages.getByRole('button', { name: 'Next' }).click();
  await expect(pages.getByRole('button', { name: 'Previous' })).toBeEnabled();
  await expect(page.getByRole('alert').filter({ hasText: saveError })).toBeVisible();
  await expect(page.getByRole('tab', { name: 'View 1 *', exact: true })).toBeVisible();
  await expect(page.locator('.saved-reference')).toHaveCount(0);
});

for (const save of [false, true]) {
  for (const queryId of [undefined, 'run-1']) {
    test(`${save ? 'Run & Save' : 'Run'} rejects a ${queryId ? 'mismatched' : 'missing'} result ID`, async ({ page }) => {
      await mockGraph(page, 'table', 'vertical', 'SELECT 1');
      let submitted = false;
      let fetches = 0;
      let refreshed = false;
      await page.route('**/*', async route => {
        if (route.request().method() !== 'POST') return route.fallback();
        const { operation, arguments: args } = route.request().postDataJSON();
        if (operation === 'view_run') {
          expect(Boolean(args.save)).toBe(save);
          submitted = true;
          return route.fulfill({ json: { status: 'success', revision: 1, query_id: queryId, save_error: 'Save refused' } });
        }
        if (submitted && operation === 'view_fetch') {
          fetches++;
          return route.fulfill({ json: { query_id: 'run-2', columns: [], rows: [] } });
        }
        if (submitted && route.request().url().endsWith('/saved-list')) refreshed = true;
        return route.fallback();
      });
      await page.goto(process.env.WORKBENCH_E2E_URL!);
      await expect(page.getByRole('grid')).toBeVisible();
      const run = page.getByRole('button', { name: save ? 'Run & Save' : /^Run Cmd/ });
      await run.click();
      if (save) await page.getByRole('dialog', { name: 'Bookmark name' }).getByRole('button', { name: 'Save', exact: true }).click();
      await expect(page.getByRole('alert').filter({ hasText: queryId
        ? 'The View result changed before it could be displayed.' : 'The completed query has no result ID.' })).toBeVisible();
      await expect(page.getByRole('alert').filter({ hasText: 'Save refused' })).toBeVisible();
      await expect(run).toBeEnabled();
      await expect(page.getByRole('grid')).toHaveCount(0);
      if (save) await expect.poll(() => refreshed).toBe(true);
      else expect(refreshed).toBe(false);
      expect(fetches).toBe(queryId ? 1 : 0);
    });
  }
}
