import { expect, type Page } from '@playwright/test';
import { browserTimeout } from './browser-deadlines';

const url = process.env.WORKBENCH_E2E_URL!;
const editor = (page: Page) => page.getByRole('textbox', { name: 'Query editor' });
const sql = `
  SELECT
    i AS row_id,
    CASE WHEN i < 4 THEN 'alpha' WHEN i < 8 THEN 'beta' ELSE 'gamma' END AS group_name,
    100 - i AS sort_value,
    repeat('😀', 180) || '-' || CAST(i AS VARCHAR) AS long_unicode,
    NULL::VARCHAR AS empty_column
  FROM range(0, 12) AS rows(i)
`;

async function workspaceUrl(page: Page) {
  const next = new URL(url);
  const workspace = `grid-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  next.searchParams.set('workspace', workspace);
  const projectRoot = next.searchParams.get('project_root');
  const endpoint = new URL(`${next.pathname.replace(/\/$/, '')}/interface`, next.origin);
  const response = await page.request.post(endpoint.toString(), {
    data: { operation: 'workspace_open', arguments: { session_id: workspace }, ...(projectRoot ? { project_root: projectRoot } : {}) },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
  return next.toString();
}

function interfaceRequest(request: { method(): string; url(): string; postDataJSON(): any }, operation?: string) {
  if (request.method() !== 'POST' || !new URL(request.url()).pathname.endsWith('/interface')) return false;
  return !operation || request.postDataJSON()?.operation === operation;
}

function fetchRequest(request: { method(): string; url(): string; postDataJSON(): any }, column?: number) {
  if (!interfaceRequest(request, 'view_fetch')) return false;
  const grid = request.postDataJSON()?.arguments?.grid;
  return column === undefined || grid?.sort?.some((item: { column?: number }) => item.column === column);
}

async function replaceSql(page: Page, value: string) {
  await editor(page).click();
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.insertText(value);
}

async function prepare(page: Page, fixedPageSize = 2, query = sql, embedded = false) {
  const target = new URL(await workspaceUrl(page));
  if (embedded) target.searchParams.set('embedded', '1');
  await page.goto(target.toString());
  await page.getByRole('tab', { name: 'Settings', exact: true }).click();
  await page.getByRole('radio', { name: 'Fixed' }).check();
  const pageSize = page.getByLabel('Fixed rows per page');
  await pageSize.fill(String(fixedPageSize));
  await pageSize.press('Tab');
  await page.getByRole('tab', { name: /^View 1/ }).click();
  await replaceSql(page, query);
}

async function run(page: Page, expectedRows = 12) {
  const request = page.waitForRequest((item) => interfaceRequest(item, 'view_run'));
  await page.keyboard.press('Meta+Enter');
  await request;
  await expect(page.getByRole('grid')).toBeVisible({ timeout: browserTimeout(15_000) });
  await expect(page.locator('.result-summary').first()).toContainText(`${expectedRows} rows`);
}

function column(page: Page, name: string) {
  return page.locator('.tabulator-col').filter({ hasText: name }).first();
}

function contrast(first: string, second: string) {
  const rgb = (value: string) => (value.match(/\d+(?:\.\d+)?/g) ?? []).slice(0, 3).map(Number).map((channel) => {
    const normalized = channel / 255;
    return normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
  });
  const luminance = (channels: number[]) => channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
  const [a, b] = [luminance(rgb(first)), luminance(rgb(second))].sort((left, right) => right - left);
  return (a + 0.05) / (b + 0.05);
}

async function openHeaderMenu(page: Page, name: string) {
  await column(page, name).click({ button: 'right' });
  const menu = page.locator('.tabulator-menu');
  await expect(menu).toBeVisible();
  return menu;
}

async function filterColumn(page: Page, name: string, value: string) {
  const menu = await openHeaderMenu(page, name);
  const dialog = page.waitForEvent('dialog').then(async (event) => {
    expect(event.message()).toContain(`Filter ${name}`);
    await event.accept(value);
  });
  const request = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
  const click = menu.locator('.tabulator-menu-item').getByText('Filter', { exact: true }).click();
  await dialog;
  await click;
  const fetched = await request;
  expect(fetched.postDataJSON()?.arguments?.grid?.filters).toEqual(expect.arrayContaining([expect.objectContaining({ value })]));
}

async function clearColumnFilter(page: Page, name: string) {
  const menu = await openHeaderMenu(page, name);
  const request = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
  await menu.locator('.tabulator-menu-item').getByText('Clear filter', { exact: true }).click();
  const fetched = await request;
  expect(fetched.postDataJSON()?.arguments?.grid?.filters).toHaveLength(1);
}

async function verifyHeaderAndFilter(page: Page) {
  const header = column(page, 'row_id');
  await expect(header.locator('.column-name')).toHaveText('row_id');
  await expect(header.locator('.column-type')).toHaveText('BIGINT');
  const styles = await header.locator('.column-type').evaluate((node) => {
    const style = getComputedStyle(node);
    return { size: Number.parseFloat(style.fontSize), opacity: style.opacity };
  });
  expect(styles.size).toBeLessThan(Number.parseFloat(await header.locator('.column-name').evaluate((node) => getComputedStyle(node).fontSize)));
  expect(styles.opacity).toBe('0.8');

  await filterColumn(page, 'group_name', 'alpha');
  await expect(page.locator('.result-summary').first()).toContainText('4 rows');
  const filterMenu = await openHeaderMenu(page, 'group_name');
  await filterMenu.locator('.tabulator-menu-item').getByText('Clear filter', { exact: true }).click();
  await expect(page.locator('.result-summary').first()).toContainText('12 rows');

}

async function verifyGroupedPages(page: Page) {
  const grouped = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch') && item.postDataJSON()?.arguments?.grid?.group_by?.column === 1);
  const groupMenu = await openHeaderMenu(page, 'group_name');
  await groupMenu.locator('.tabulator-menu-item').getByText('Group by', { exact: true }).click();
  await grouped;
  await expect(page.locator('.tabulator-group')).toContainText('group_name: alpha (4)');
  await expect(page.locator('.tabulator-group')).not.toContainText('beta');

  const next = page.getByRole('navigation', { name: 'Result pages' }).getByRole('button', { name: 'Next' });
  for (let index = 0; index < 2; index += 1) {
    const request = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
    await next.click();
    await request;
    const first = 3 + index * 2;
    await expect(page.locator('.result-summary').first()).toContainText(`showing ${first}-${first + 1}`);
  }
  await expect(page.locator('.tabulator-group')).toContainText('group_name: beta (4)');

}

async function verifyGlobalGrid(page: Page, embedded: boolean) {
  let runs = 0;
  page.on('request', (request) => { if (interfaceRequest(request, 'view_run')) runs += 1; });
  await prepare(page, 2, sql, embedded);
  await run(page);
  await verifyHeaderAndFilter(page);

  const sortedGlobally = page.waitForRequest((item) => fetchRequest(item, 2));
  const sortMenu = await openHeaderMenu(page, 'sort_value');
  await expect(sortMenu.locator('.tabulator-menu-item')).toHaveText([
    'Column Sort ascending', 'Column Sort descending', 'Group by', 'Filter', 'Clear filter',
  ]);
  await sortMenu.locator('.tabulator-menu-item').getByText('Column Sort descending', { exact: true }).click();
  await sortedGlobally;
  await expect(page.locator('.tabulator-row').first().locator('.tabulator-cell').nth(2)).toHaveText('100');
  const sortedNext = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
  await page.getByRole('navigation', { name: 'Result pages' }).getByRole('button', { name: 'Next' }).click();
  await sortedNext;
  await expect(page.locator('.tabulator-row').first().locator('.tabulator-cell').nth(2)).toHaveText('98');

  await verifyGroupedPages(page);

  await page.keyboard.press('Meta+P');
  const palette = page.getByRole('dialog', { name: 'Command palette' });
  await palette.getByRole('textbox').fill('Result grid: Sort column descending');
  const sorted = page.waitForRequest((item) => fetchRequest(item, 1));
  const prompt = page.waitForEvent('dialog').then(async (dialog) => {
    expect(dialog.message()).toContain('Result column index');
    await dialog.accept('1');
  });
  const enter = page.keyboard.press('Enter');
  await prompt;
  await enter;
  await sorted;
  expect(runs).toBe(1);
}


export { verifyGlobalGrid, prepare, run, interfaceRequest, filterColumn, clearColumnFilter, column, fetchRequest, openHeaderMenu, contrast };
