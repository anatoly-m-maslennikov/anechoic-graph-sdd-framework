import { expect, test, type Page } from '@playwright/test';
import { browserTimeout } from './browser-deadlines';
import { toolRequest } from './tool_rest_fixture';
import { url, editor, projectName, replaceSql,
  runSql, sharedWorkspace, persistedAdaptiveWorkspace,
  openSharedPages, renameAndRestoreView,
    verifyEmbeddedDensity } from './workbench-fixture';

async function runLatestDraft(secondPage: Page,
  releaseUpdate: (() => void) | undefined) {
  await replaceSql(secondPage, 'SELECT 2 AS latest_draft');
  const run = runSql(secondPage);
  releaseUpdate?.();
  await run;
  await expect(editor(secondPage)).toContainText('SELECT 2 AS latest_draft');
  await expect(secondPage.getByRole('grid')).toBeVisible(
    { timeout: browserTimeout(12_000) });
  await expect(secondPage.getByRole('columnheader').first(
    )).toHaveText(/latest_draft\s*INTEGER/);
}

test('binds two browser contexts to one Workspace and observes external state',
  async ({ browser }) => {
  const setup = await sharedWorkspace();
  const firstContext = await browser.newContext();
  const secondContext = await browser.newContext();
  const firstPage = await firstContext.newPage();
  const secondPage = await secondContext.newPage();
  let releaseUpdate: (() => void) | undefined;
  try {
    await test.step('open both contexts with the externally focused View', async () => {
      await openSharedPages(firstPage, secondPage, setup.workspaceUrl);
    });
    let updateStarted!: () => void;
    const held = new Promise<void>((resolve) => releaseUpdate = resolve);
    const started = new Promise<void>((resolve) => updateStarted = resolve);
    let delayed = false;
    await test.step('hold the first foreground autosave', async () => {
      await secondPage.route('**/tools', async (route) => {
        const request = toolRequest(route);
        if (!delayed && request?.name === 'view_update' && request.arguments.view_id === setup.externalId &&
          request.arguments.sql === 'SELECT 1 AS first_draft') {
          delayed = true;
          const response = await route.fetch();
          updateStarted(); await held;
          await route.fulfill({ response });
          return;
        }
        await route.fallback();
      });
      await secondPage.bringToFront();
      await secondPage.evaluate(() => new Promise<void>((resolve) => requestAnimationFrame(() => resolve())));
      await expect(editor(secondPage)).toBeEditable();
      await replaceSql(secondPage, 'SELECT 1 AS first_draft');
      await expect(editor(secondPage)).toContainText('SELECT 1 AS first_draft');
      await firstPage.bringToFront();
      await secondPage.bringToFront();
      await started;
    });
    await test.step('run the draft edited while the first autosave is held', async () => {
      await runLatestDraft(secondPage, releaseUpdate);
    });
  } finally {
    releaseUpdate?.();
    await Promise.all([firstContext.close(), secondContext.close()]);
  }
});
test('waits for the initial Workspace binding before accepting SQL input',
  async ({ page }) => {
  let releaseOpen!: () => void;
  let opened!: () => void;
  const held = new Promise<void>((resolve) => releaseOpen = resolve);
  const openStarted = new Promise<void>((resolve) => opened = resolve);
  await page.route('**/tools', async (route) => {
    if (toolRequest(route)?.name === 'workspace_open') {
      const response = await route.fetch();
      opened(); await held;
      await route.fulfill({ response });
      return;
    }
    await route.fallback();
  });
  try {
    await page.goto(url); await openStarted;
    await expect(editor(page)).toHaveAttribute('contenteditable', 'false');
    await expect(editor(page)).toHaveAttribute('aria-readonly', 'true');
    await expect(page.getByRole('button', {
      name: 'Run Cmd+Enter' })).toBeDisabled();
    releaseOpen();
    await expect(editor(page)).toBeEditable();
    await expect(editor(page)).toHaveAttribute('aria-readonly', 'false');
    await replaceSql(page, 'SELECT 31 AS bound_input');
    const run = page.waitForRequest((request) => request.method(
      ) === 'POST' && request.url().endsWith('/tools')
      && request.postDataJSON()?.name === 'view_run');
    await runSql(page); await run;
    await expect(page.getByRole('grid')).toBeVisible();
  } finally { releaseOpen?.(); }
});
test(
  'opens, leaves, and rebuilds a cached adaptive result without an uncaught Tabulator lifecycle error',
  async ({ page }) => {
  const workspaceUrl = await persistedAdaptiveWorkspace(
    ); const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  const fetched = page.waitForResponse((response) =>
    response.request().method() === 'POST' && response.url().endsWith('/tools')
    && response.request().postDataJSON(
      )?.name === 'view_fetch' && response.status() === 200);
  await page.goto(workspaceUrl); await fetched;
  await expect(page.getByRole('grid')).toBeVisible();
  await expect(page.locator('.result-summary')).toContainText(
    '20 rows, 3 of 4 columns');
  await page.getByRole('tab', { name: 'Settings', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Settings' })).toBeVisible();
  await page.getByRole('tab', { name: 'View 1', exact: true }).click();
  await expect(page.getByRole('grid')).toBeVisible();
  await page.evaluate(() => new Promise<void>((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
  expect(errors).toEqual([]);
});

test(
  'keeps dirty SQL through Run and Check under the Project Workbench header',
  async ({ page }) => {
  await page.goto(url);
  const layout = await page.locator('.workspace').evaluate((node) => ({
    width: node.getBoundingClientRect().width, viewport: innerWidth }));
  expect(layout.width).toBeGreaterThan(layout.viewport * 0.9);
  const header = page.locator('header');
  await expect(header.getByText('Workbench', { exact: true })).toBeVisible();
  await expect(header.getByText(`Project: ${projectName}`,
    { exact: true })).toBeVisible();
  await expect(header.getByRole('tab', { name:
    'Settings', exact: true })).toBeVisible();
  await expect(header.getByRole('tab', { name:
    'Bookmarks and saved Views' })).toBeVisible();
  await expect(page.getByText('Query editor', { exact: true })).toBeVisible();
  await replaceSql(page,
    'SELECT reference FROM atoms ORDER BY reference LIMIT 1');
  await runSql(page);
  await expect(page.getByRole('grid')).toBeVisible();
  await expect(page.getByRole('grid').getByRole('row')).toHaveCount(2);
  await expect(page.getByRole('columnheader').first(
    )).toHaveText(/reference\s*VARCHAR/);
  await page.getByRole('button', { name: /^Check/ }).click();
  await expect(page.getByText('Valid: 1 rows, 1 columns.')).toBeVisible();
  await expect(page.getByRole('tab', { name: /^View 1 \*/ })).toBeVisible();
  await page.getByRole('button', { name: 'Run & Save', exact: true }).click();
  const queryName = page.getByRole('dialog', {
    name: 'Bookmark name' }).getByRole('textbox');
  await queryName.fill('E2E query');
  await queryName.press('Enter');
  await expect(page.locator('.panel-heading').getByText(
    /^Saved:/)).toBeVisible();
  await expect(editor(page)).toContainText(
    'SELECT reference FROM atoms ORDER BY reference LIMIT 1');
  await expect(page.getByRole('tab', { name:
    'View 1', exact: true })).toBeVisible();
});

test('reports Check for the current SQL while retaining earlier result rows',
  async ({ page }) => {
  await page.goto(url);
  const verdict = page.getByRole('status', { name: 'Query check' });
  const check = page.getByRole('button', { name: /^Check/ });
  await expect(verdict).toHaveText('Not checked');
  await replaceSql(page, 'SELECT 7 AS earlier_result');
  await runSql(page);
  await expect(page.getByRole('columnheader')).toHaveText(/earlier_result/);
  await check.click();
  await expect(verdict).toHaveText('Valid: 1 rows, 1 columns.');
  await replaceSql(page, 'SELECT FROM');
  await expect(verdict).toHaveText('Not checked');
  await check.click();
  await expect(verdict).toContainText('Invalid:');
  await expect(verdict).not.toContainText('Valid:');
  await expect(page.getByRole('columnheader')).toHaveText(/earlier_result/);
});

test('clears a Check verdict when the shared Workspace updates SQL',
  async ({ page }) => {
  const shared = await sharedWorkspace();
  await page.goto(shared.workspaceUrl);
  const verdict = page.getByRole('status', { name: 'Query check' });
  await expect(editor(page)).toHaveText('SELECT 42 AS external_value');
  await page.getByRole('button', { name: /^Check/ }).click();
  await expect(verdict).toHaveText('Valid: 1 rows, 1 columns.');

  const workspaceId = new URL(
    shared.workspaceUrl).searchParams.get('workspace');
  await shared.call('view_update', {
    workspace_id: workspaceId, view_id: shared.externalId,
      sql: 'SELECT 43 AS external_value',
    expected_revision: shared.revision, cursor_position: 0,
  });
  await expect(editor(page)).toHaveText('SELECT 43 AS external_value',
    { timeout: browserTimeout(10_000) });
  await expect(verdict).toHaveText('Not checked');
});
