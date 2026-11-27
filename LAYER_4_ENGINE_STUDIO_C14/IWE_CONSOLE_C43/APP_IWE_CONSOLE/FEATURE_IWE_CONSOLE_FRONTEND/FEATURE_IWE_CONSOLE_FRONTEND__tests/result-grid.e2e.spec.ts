import { expect, test, type Page } from '@playwright/test';
import { verifyGlobalGrid, prepare, run, interfaceRequest, filterColumn, clearColumnFilter, column, fetchRequest, openHeaderMenu, contrast } from './result-grid-fixture';

test('keeps filtering, sorting and grouping global while paging the cached standalone result', ({ page }) => verifyGlobalGrid(page, false));
test('keeps filtering, sorting and grouping global while paging the cached embedded result', ({ page }) => verifyGlobalGrid(page, true));

test('keeps another column filter when one column filter is cleared', async ({ page }) => {
  let runs = 0;
  page.on('request', (request) => { if (interfaceRequest(request, 'view_run')) runs += 1; });
  await prepare(page, 4);
  await run(page);
  await filterColumn(page, 'group_name', 'beta');
  await filterColumn(page, 'row_id', '5');
  await expect(page.locator('.result-summary').first()).toContainText('1 rows');
  await clearColumnFilter(page, 'group_name');
  await expect(page.locator('.result-summary').first()).toContainText('1 rows');
  expect(runs).toBe(1);
});

test('keeps SQL NULL and the literal null in separate groups', async ({ page }) => {
  const query = `
    SELECT CASE WHEN i < 2 THEN NULL::VARCHAR ELSE 'null' END AS group_value
    FROM range(0, 3) AS rows(i)
  `;
  await prepare(page, 3, query);
  await run(page, 3);
  const grouped = page.waitForRequest((item) => (
    interfaceRequest(item, 'view_fetch')
    && item.postDataJSON()?.arguments?.grid?.group_by?.column === 0
  ));
  const menu = await openHeaderMenu(page, 'group_value');
  await menu.locator('.tabulator-menu-item').getByText('Group by', { exact: true }).click();
  await grouped;
  await expect.poll(async () => page.locator('[role="rowgroup"]').evaluateAll((nodes) => nodes
    .map((node) => node.textContent?.trim() ?? '')
    .filter((text) => /^group_value: (?:NULL|null) \(\d+\)$/.test(text))))
    .toEqual(expect.arrayContaining(['group_value: NULL (2)', 'group_value: null (1)']));
});

test('keeps dotted SQL column names as labels without using them as Tabulator fields', async ({ page }) => {
  await prepare(page, 1, `
    SELECT
      'CA-R-1' AS "header.identity.atom_id",
      'Method' AS "header.context.role",
      'Active' AS "header.state.status",
      'formal' AS "content.claim.formal_claim"
  `);
  await run(page, 1);
  for (const name of ['header.identity.atom_id', 'header.context.role', 'header.state.status', 'content.claim.formal_claim']) {
    await expect(column(page, name).locator('.column-name')).toHaveText(name);
  }
  await expect(page.locator('.tabulator-row').first().locator('.tabulator-cell')).toHaveText(['CA-R-1', 'Method', 'Active', 'formal']);
  const sorted = page.waitForRequest((item) => fetchRequest(item, 0));
  const menu = await openHeaderMenu(page, 'header.identity.atom_id');
  await menu.locator('.tabulator-menu-item').getByText('Column Sort ascending', { exact: true }).click();
  await sorted;
});

test('keeps Tabulator header and data rows legible in light and dark themes', async ({ page }) => {
  await prepare(page, 1, "SELECT 'visible value' AS value");
  await run(page, 1);
  async function colors(theme: 'light' | 'dark') {
    await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    await page.getByLabel('Theme').selectOption(theme);
    await page.getByRole('tab', { name: /^View 1/ }).click();
    await expect(page.getByRole('grid')).toBeVisible();
    const row = page.locator('.tabulator-row').first();
    await row.hover();
    return page.locator('.result-grid').evaluate((grid) => {
      const header = grid.querySelector<HTMLElement>('.tabulator-col')!;
      const type = header.querySelector<HTMLElement>('.column-type')!;
      const row = grid.querySelector<HTMLElement>('.tabulator-row')!;
      row.classList.add('tabulator-selected');
      const cell = row.querySelector<HTMLElement>('.tabulator-cell')!;
      const result = {
        header: getComputedStyle(header), row: getComputedStyle(row), cell: getComputedStyle(cell),
      };
      row.classList.remove('tabulator-selected');
      return {
        header: { color: result.header.color, background: result.header.backgroundColor },
        type: { color: getComputedStyle(type).color, background: result.header.backgroundColor },
        row: { color: result.row.color, background: result.row.backgroundColor },
        cell: { color: result.cell.color, background: result.row.backgroundColor },
      };
    });
  }
  for (const theme of ['light', 'dark'] as const) {
    const themed = await colors(theme);
    expect(contrast(themed.header.color, themed.header.background)).toBeGreaterThan(4.5);
    expect(contrast(themed.type.color, themed.type.background)).toBeGreaterThan(4.5);
    expect(contrast(themed.row.color, themed.row.background)).toBeGreaterThan(4.5);
    expect(contrast(themed.cell.color, themed.cell.background)).toBeGreaterThan(4.5);
  }
});

test('keeps source newlines in cells and the full-value dialog', async ({ page }) => {
  await prepare(page, 1, "SELECT 'first line' || chr(10) || 'second line' AS content_claim");
  await run(page, 1);
  const cell = page.locator('.tabulator-row').first().locator('.tabulator-cell').first();
  await expect(cell).toContainText('first line\nsecond line');
  await expect(cell.locator('.cell-value')).toHaveCSS('white-space', 'pre-wrap');
  await cell.click({ button: 'right' });
  let message = '';
  page.once('dialog', async (dialog) => { message = dialog.message(); await dialog.accept(); });
  await page.locator('.tabulator-menu-item').getByText('Cell Show full value', { exact: true }).click();
  expect(message).toBe('first line\nsecond line');
});

async function verifyFullValueAndCopy(page: Page) {
  const longCell = page.locator('.tabulator-row').first().locator('.tabulator-cell').nth(3);
  await longCell.click({ button: 'right' });
  const fullValue = page.waitForEvent('dialog');
  const showFull = page.locator('.tabulator-menu-item').getByText('Cell Show full value', { exact: true }).click();
  const fullDialog = await fullValue;
  expect(Array.from(fullDialog.message()).length).toBeGreaterThan(150);
  expect(fullDialog.message()).toContain('😀');
  await fullDialog.dismiss();
  await showFull;

  await page.locator('.tabulator-row').first().locator('.tabulator-cell').first().click({ button: 'right' });
  const copy = page.locator('.tabulator-menu-item').getByText('Row Copy row', { exact: true });
  await copy.click();
  const copied = JSON.parse(await page.evaluate(() => navigator.clipboard.readText())) as unknown[];
  expect(copied).toHaveLength(5);
  expect(copied[4]).toBeNull();
  expect(Array.from(String(copied[3])).length).toBeGreaterThan(150);

}

test('preserves full Unicode values and hidden columns in row actions, with zoomed menus', async ({ browser }) => {
  const context = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await context.newPage();
  let runs = 0;
  page.on('request', (request) => { if (interfaceRequest(request, 'view_run')) runs += 1; });
  try {
    await prepare(page, 4);
    await run(page);
    expect(runs).toBe(1);

    await verifyFullValueAndCopy(page);

    await column(page, 'row_id').click({ button: 'right' });
    const baselineMenu = page.locator('.tabulator-menu');
    const baselineFontSize = await baselineMenu.evaluate((node) => getComputedStyle(node).fontSize);
    const baselineWidth = (await baselineMenu.boundingBox())!.width;
    const baselineSort = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
    await baselineMenu.locator('.tabulator-menu-item').getByText('Column Sort ascending', { exact: true }).click();
    await baselineSort;
    await page.keyboard.press('Meta+P');
    const palette = page.getByRole('dialog', { name: 'Command palette' });
    await palette.getByRole('textbox').fill('Interface text zoom: 125%');
    await page.keyboard.press('Enter');
    await column(page, 'row_id').click({ button: 'right' });
    const menu = page.locator('.tabulator-menu');
    const zoomedFontSize = await menu.evaluate((node) => getComputedStyle(node).fontSize);
    expect(zoomedFontSize).not.toBe(baselineFontSize);
    expect(await menu.locator('.tabulator-menu-item').count()).toBe(5);
    const textZoomSort = page.waitForRequest((item) => interfaceRequest(item, 'view_fetch'));
    await menu.locator('.tabulator-menu-item').getByText('Column Sort ascending', { exact: true }).click();
    await textZoomSort;
    await page.keyboard.press('Meta+P');
    await page.getByRole('dialog', { name: 'Command palette' }).getByRole('textbox').fill('Interface zoom: 125%');
    await page.keyboard.press('Enter');
    await column(page, 'row_id').click({ button: 'right' });
    expect((await page.locator('.tabulator-menu').boundingBox())!.width).toBeGreaterThan(baselineWidth * 1.1);

    expect(runs).toBe(1);
  } finally {
    await context.close();
  }
});
