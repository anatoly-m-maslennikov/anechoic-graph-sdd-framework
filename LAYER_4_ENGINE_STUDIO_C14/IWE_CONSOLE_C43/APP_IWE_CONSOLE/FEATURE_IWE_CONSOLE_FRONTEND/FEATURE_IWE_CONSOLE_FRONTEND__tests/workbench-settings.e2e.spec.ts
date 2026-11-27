import { expect, test, type Page } from '@playwright/test';
import { url, editor, projectName, replaceSql,
  runSql, sharedWorkspace, persistedAdaptiveWorkspace,
  openSharedPages, renameAndRestoreView,
    verifyEmbeddedDensity } from './workbench-fixture';

test('restores local View state and opens a saved View without running it',
  async ({ page }) => {
  await page.goto(url);
  await renameAndRestoreView(page);
  await page.getByRole('button', { name: 'Save View', exact: true }).click();
  const queryHeader = page.locator('.panel-heading');
  await expect(queryHeader.getByText(
    'Query editor', { exact: true })).toBeVisible();
  await expect(queryHeader.getByText(/^Saved:/)).toBeVisible();
  const saved = queryHeader.getByRole('link');
  await expect(saved).toBeVisible();
  const href = await saved.getAttribute('href');
  expect(href).toContain('?query=');
  const id = new URL(href!, url).searchParams.get('query');
  let executionRequests = 0;
  page.on('request', (request) => {
    if (request.method() === 'POST' && request.url().endsWith('/tools') &&
      /^(view|query)_(run|check)$/.test(request.postDataJSON()?.name)) {
      executionRequests += 1;
    }
  });
  await expect(page.getByRole('button', { name:
    'Open Saved', exact: true })).toHaveCount(0);
  await page.keyboard.press('Meta+P');
  await page.getByRole('dialog', { name:
    'Command palette' }).getByRole('textbox').fill('Open Saved');
  await page.keyboard.press('Enter');
  const referenceInput = page.getByRole('dialog', { name:
    'Open Bookmark or saved View' }).getByRole('textbox');
  await expect(referenceInput).toBeFocused();
  await referenceInput.fill(id!);
  await page.keyboard.press('Enter');
  await expect(editor(page)).toContainText("SELECT 'saved worksheet'");
  await expect(page.getByRole('grid')).toHaveCount(0);
  expect(executionRequests).toBe(0);
});

async function changePresentationSettings(page: Page) {
  await page.keyboard.press('Meta+P');
  const palette = page.getByRole('dialog', { name: 'Command palette' });
  await palette.getByRole('textbox').fill('Interface text zoom: 125%');
  await page.keyboard.press('Enter');
  await expect.poll(() => page.evaluate(() => getComputedStyle(
    document.documentElement).getPropertyValue(
      '--interface-text-scale').trim())).toBe('1.25');
  await expect(palette).toBeHidden();
  await page.keyboard.press('Meta+P');
  await page.getByRole('dialog', { name: 'Command palette' }).getByRole(
    'textbox').fill('Content text zoom: 150%');
  await page.keyboard.press('Enter');
  await expect.poll(() => page.evaluate(() => getComputedStyle(
    document.documentElement).getPropertyValue(
      '--content-text-scale').trim())).toBe('1.5');
  await expect(palette).toBeHidden();
  await page.getByLabel('Interface zoom').selectOption('90');
  await page.getByLabel('Density').selectOption('compact');
  await expect.poll(() => page.evaluate(() => ({ density:
    document.documentElement.dataset.density, interface:
    getComputedStyle(document.documentElement).getPropertyValue(
      '--interface-scale').trim() }))).toEqual({ density: 'compact',
        interface: '0.9' });
}

async function checkInitialAppearance(page: Page) {
  await expect.poll(() => page.evaluate(() => ({
    theme: document.documentElement.dataset.theme,
    density: document.documentElement.dataset.density,
    interfaceText: getComputedStyle(document.documentElement)
      .getPropertyValue('--interface-text-scale').trim(),
    contentText: getComputedStyle(document.documentElement)
      .getPropertyValue('--content-text-scale').trim(),
    interface: getComputedStyle(document.documentElement)
      .getPropertyValue('--interface-scale').trim(),
  }))).toEqual({
    theme: 'system', density: 'comfortable', interfaceText: '1',
    contentText: '1', interface: '1',
  });
}

test('shows native source indexing status and keeps settings independent',
  async ({ browser }) => {
  const standalone = await browser.newContext();
  const page = await standalone.newPage();
  try {
    const statusResponse = page.waitForResponse((response) =>
      response.request().method() === 'POST' &&
      response.url().endsWith('/tools') && response.ok() &&
      response.request().postDataJSON()?.name === 'iwe_console_status');
    await page.goto(url);
    const envelope = await (await statusResponse).json();
    expect(envelope.result?.value?.mode).toBe('live_index');
    await expect(page.getByRole('status', { name: 'Source indexing status'
      })).toHaveText('Source index: Watching files');
    await checkInitialAppearance(page);

    await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    const settings = page.getByRole('region', { name: 'Settings' });
    await expect(settings.getByLabel('Theme')).toHaveValue('system');
    await expect(settings.getByLabel('Interface text zoom')).toHaveValue(
      '100');
    await expect(settings.getByLabel('Content text zoom')).toHaveValue('100');
    await expect(settings.getByLabel('Interface zoom')).toHaveValue('100');
    await expect(settings.getByLabel('Density')).toHaveValue('comfortable');
    const y = await Promise.all(['Theme', 'Interface text zoom',
      'Content text zoom', 'Interface zoom',
      'Density'].map(async (name) => (await settings.getByLabel(
        name).boundingBox())?.y));
    expect(y[0]).toBeLessThan(y[1]!); expect(y[1]).toBeLessThan(y[2]!);
      expect(y[2]).toBeLessThan(y[3]!); expect(y[3]).toBeLessThan(y[4]!);

    await changePresentationSettings(page);
    await page.reload();
    await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    await expect(page.getByLabel('Interface text zoom')).toHaveValue('125');
    await expect(page.getByLabel('Content text zoom')).toHaveValue('150');
    await expect(page.getByLabel('Interface zoom')).toHaveValue('90');
    await expect(page.getByLabel('Density')).toHaveValue('compact');
  } finally { await standalone.close(); }

  await verifyEmbeddedDensity(browser);
});

test('scales interface and query content text independently',
  async ({ page }) => {
  await page.goto(url);
  const sizes = () => page.evaluate(() => ({
    title: Number.parseFloat(getComputedStyle(
      document.querySelector('.app-name')!).fontSize),
    editor: Number.parseFloat(getComputedStyle(
      document.querySelector('.cm-content')!).fontSize),
  }));
  const initial = await sizes();
  await page.getByRole('tab', { name: 'Settings', exact: true }).click();
  await page.getByLabel('Interface text zoom').selectOption('125');
  await page.getByRole('tab', { name: /^View 1/ }).click();
  const interfaceZoomed = await sizes();
  expect(interfaceZoomed.title).toBeGreaterThan(initial.title);
  expect(interfaceZoomed.editor).toBe(initial.editor);
  await page.getByRole('tab', { name: 'Settings', exact: true }).click();
  await page.getByLabel('Content text zoom').selectOption('150');
  await page.getByRole('tab', { name: /^View 1/ }).click();
  const contentZoomed = await sizes();
  expect(contentZoomed.title).toBe(interfaceZoomed.title);
  expect(contentZoomed.editor).toBeGreaterThan(interfaceZoomed.editor);
});

test(
  'uses persisted adaptive or fixed display and global grid actions without rerunning SQL',
  async ({ browser }) => {
  const context = await browser.newContext(); const page = await context.newPage(); let runs = 0;
  page.on('request', (request) => { if (request.method() === 'POST' && new URL(request.url(
    )).pathname.endsWith('/tools') && request.postDataJSON()?.name === 'view_run') runs += 1; });
  try {
    await page.goto(url);
    await replaceSql(page, "SELECT i AS ordinal, repeat('😀', 151) AS long_value FROM range(0, 220) AS t(i)");
    await runSql(page);
    await expect(page.getByRole('grid')).toBeVisible(); await expect(
      page.getByLabel('Result cell content')).toHaveValue('limited');
    expect(runs).toBe(1);
    await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    await expect(page.getByRole('radio', { name: 'Adaptive' })).toBeChecked();
    await expect(page.getByRole('radio', { name: 'Limited' })).toBeChecked();
    await expect(page.getByLabel('Fixed rows per page')).toHaveCount(0);
    await page.getByRole('radio', { name: 'Fixed' }).check();
    const rows = page.getByLabel('Fixed rows per page'); await expect(rows).toHaveValue('100');
    const fixedPage = page.waitForRequest((request) => request.method() === 'POST' &&
      request.url().endsWith('/tools') && request.postDataJSON()?.name === 'view_fetch' &&
      request.postDataJSON()?.arguments?.page_size === 25);
    await rows.fill('25'); await fixedPage;
    await page.getByRole('tab', { name: /^View 1/ }).click();
    await expect(page.locator('.result-summary')).toContainText('220 rows');
    await expect(page.getByRole('navigation', { name: 'Result pages' })).toBeInViewport();
    await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    await page.getByRole('radio', { name: 'Adaptive' }).check(); await expect(rows).toHaveCount(0);
    await page.getByRole('tab', { name: /^View 1/ }).click();
    await page.getByLabel('Result cell content').selectOption('full');
    await expect(page.getByLabel('Inline content character limit')).toHaveCount(0);
    expect(runs).toBe(1);

    const cell = page.locator('.tabulator-row .tabulator-cell').nth(1);
    await cell.click({ button: 'right' });
    await expect(page.locator('.tabulator-menu-item')).toHaveText(['Cell Copy value', 'Cell Show full value', 'Row Copy row']);
    await page.getByText('Cell Copy value', { exact: true }).click();
    const header = page.getByRole('columnheader').first(); await header.click({ button: 'right' });
    await expect(page.locator('.tabulator-menu-item')).toHaveText(['Column Sort ascending',
      'Column Sort descending', 'Group by', 'Filter', 'Clear filter']);
    const sort = page.waitForRequest((request) => request.method() === 'POST' &&
      request.url().endsWith('/tools') && request.postDataJSON()?.name === 'view_fetch' &&
      request.postDataJSON()?.arguments?.grid?.sort?.[0]?.direction === 'desc');
    await page.getByText('Column Sort descending', { exact: true }).click(); await sort;
    expect(runs).toBe(1);
    await page.reload(); await page.getByRole('tab', { name: 'Settings', exact: true }).click();
    await expect(page.getByRole('radio', { name: 'Adaptive' })).toBeChecked();
      await expect(page.getByRole('radio', { name: 'Full' })).toBeChecked();
  } finally { await context.close(); }
});

test('keeps NULL and text null group counts distinct', async ({ page }) => {
  await page.goto(url);
  await replaceSql(page,
    "SELECT CASE WHEN i < 2 THEN NULL::VARCHAR ELSE 'null' END AS marker FROM range(0, 5) AS t(i)");
  await runSql(page); await expect(page.getByRole('grid')).toBeVisible();
  const grouped = page.waitForRequest((
    request) => request.method() === 'POST' && request.url().endsWith('/tools') &&
    request.postDataJSON()?.name === 'view_fetch' &&
      request.postDataJSON()?.arguments?.grid?.group_by?.column === 0);
  await page.getByRole('columnheader').first().click({ button: 'right' });
  await page.getByText('Group by', { exact: true }).click(); await grouped;
  await expect(page.locator('.tabulator-group').filter(
    { hasText: 'marker: NULL (2)' })).toHaveCount(1);
  await expect(page.locator('.tabulator-group').filter(
    { hasText: 'marker: null (3)' })).toHaveCount(1);
});

test(
  'uses palette navigation, quoted status completion, and focus after hiding the editor',
  async ({ page }) => {
  const schemaResponse = page.waitForResponse((response) => (
    response.request().method() === 'POST'
    && new URL(response.url()).pathname.endsWith('/tools')
    && response.request().postDataJSON()?.name === 'query_schema'
    && response.status() === 200
  ));
  await page.goto(url);
  const envelope = await (await schemaResponse).json();
  const schema = envelope.result.value as {
    tables: { atoms: Array<{ name: string; values?: string[] }> };
  };
  expect(schema.tables.atoms.find((column) => column.name === 'header.state.status')?.values).toContain('active');
  await page.keyboard.press('Meta+P');
  const palette = page.getByRole('dialog', { name: 'Command palette' });
  await expect(palette.getByRole('textbox')).toBeFocused();
  await page.keyboard.press('Control+N');
  await page.keyboard.press('Enter');
  await expect(palette).toBeHidden();
  await expect(page.getByRole('region', { name: 'Bookmarks and saved Views' })).toBeVisible();
  await page.keyboard.press('Meta+P');
  await expect(palette).toBeVisible();
  await expect(palette.getByRole('textbox')).toBeFocused();
  await page.keyboard.press('Control+N');
  await page.keyboard.press('Control+P');
  await page.keyboard.press('Enter');
  await expect(palette).toBeHidden();
  await expect(page.getByRole('region', { name: 'Settings' })).toBeVisible();
  await page.getByRole('tab', { name: /^View 1/ }).click();
  await replaceSql(page, "SELECT \"header.state.status\" FROM atoms WHERE \"header.state.status\" = 'act'");
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('Control+Space');
  const active = page.getByRole('option', { name: 'active', exact: true });
  await expect(active).toBeVisible();
  await active.click();
  await expect(editor(page)).toContainText("header.state.status\" = 'active'");
  const editorToggle = page.getByRole('button', { name: /Query editor.*Hide editor/ });
  await expect(editorToggle).toHaveAttribute('aria-expanded', 'true');
  await editorToggle.click();
  await expect(page.getByRole('button', { name: /Query editor.*Show editor/ })).toHaveAttribute('aria-expanded', 'false');
  await page.keyboard.press('Meta+P');
  await expect(palette).toBeVisible();
  await expect(palette.getByRole('textbox')).toBeFocused();
  await palette.getByRole('textbox').fill('Focus Query editor');
  await page.keyboard.press('Enter');
  await expect(editor(page)).toBeFocused();
});
