
import { expect, test } from '@playwright/test';
import { replaceSql } from './workbench-fixture';

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
