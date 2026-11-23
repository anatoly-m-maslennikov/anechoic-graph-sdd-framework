
import { expect, type Page, type Browser } from '@playwright/test';

const url = process.env.WORKBENCH_E2E_URL!;
const editor = (page: Page) => page.getByRole('textbox', { name: 'Query editor' });
const projectName = new URL(url).pathname.split('/').filter(Boolean).at(-1)!;

async function replaceSql(page: Page, sql: string) {
  const input = editor(page);
  await expect(input).toBeEditable();
  await expect(input).toHaveAttribute('contenteditable', 'true');
  await input.click();
  await input.press('ControlOrMeta+A');
  await input.pressSequentially(sql);
  await expect(input).toContainText(sql);
}
async function runSql(page: Page) { await editor(page).press('Meta+Enter'); }

async function sharedWorkspace() {
  const workspace = `browser-${Date.now()}`;
  const workspaceUrl = new URL(url);
  workspaceUrl.searchParams.set('workspace', workspace);
  const endpoint = new URL(`${workspaceUrl.pathname.replace(/\/$/, '')}/interface`, workspaceUrl.origin).toString();
  const projectRoot = workspaceUrl.searchParams.get('project_root');
  const call = async (operation: string, arguments_: Record<string, unknown>) => {
    const response = await fetch(endpoint, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation, arguments: arguments_, ...(projectRoot ? { project_root: projectRoot } : {}) }),
    });
    expect(response.ok, `${operation} failed`).toBeTruthy();
    return response.json() as Promise<Record<string, any>>;
  };
  const opened = await call('workspace_open', { session_id: workspace });
  const created = await call('view_create', { workspace_id: workspace, position: 'last', name: 'External View' });
  const externalId = created.view_id as string;
  const external = created.views.find((item: { id: string }) => item.id === externalId);
  const updated = await call('view_update', { workspace_id: workspace, view_id: externalId, sql: 'SELECT 42 AS external_value', expected_revision: external.revision, cursor_position: 0 });
  await call('view_focus', { workspace_id: workspace, view_id: externalId });
  await call('view_run', { workspace_id: workspace, view_id: externalId, cursor_position: 0 });
  return { externalId, revision: updated.revision as number, workspaceUrl: workspaceUrl.toString(), call };
}

async function persistedAdaptiveWorkspace() {
  const workspace = `cached-grid-${Date.now()}`;
  const workspaceUrl = new URL(url); workspaceUrl.searchParams.set('workspace', workspace);
  const endpoint = new URL(`${workspaceUrl.pathname.replace(/\/$/, '')}/interface`, workspaceUrl.origin).toString();
  const projectRoot = workspaceUrl.searchParams.get('project_root');
  const call = async (operation: string, arguments_: Record<string, unknown>) => {
    const response = await fetch(endpoint, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation, arguments: arguments_, ...(projectRoot ? { project_root: projectRoot } : {}) }),
    });
    expect(response.ok, `${operation} failed`).toBeTruthy();
    return response.json() as Promise<Record<string, any>>;
  };
  const opened = await call('workspace_open', { session_id: workspace }); const view = opened.views[0];
  await call('view_update', {
    workspace_id: workspace, view_id: view.id,
    sql: "SELECT i AS row_id, CASE WHEN i % 2 = 0 THEN 'alpha' ELSE 'beta' END AS group_name, 20 - i AS sort_value, NULL::VARCHAR AS empty_column FROM range(0, 20) AS rows(i)",
    expected_revision: view.revision, cursor_position: 0,
  });
  await call('view_run', { workspace_id: workspace, view_id: view.id, cursor_position: 0 });
  return workspaceUrl.toString();
}

async function openSharedPages(firstPage: Page, secondPage: Page, workspaceUrl: string) {
  await Promise.all([firstPage.goto(workspaceUrl), secondPage.goto(workspaceUrl)]);
  const external = firstPage.getByRole('tab', { name: 'External View', exact: true });
  await expect(external).toBeVisible({ timeout: 12_000 });
  await expect(external).toHaveAttribute('aria-selected', 'true');
  await expect(firstPage.getByRole('textbox', { name: 'Query editor' })).toContainText('SELECT 42 AS external_value');
  await expect(firstPage.getByRole('grid')).toBeVisible({ timeout: 12_000 });
  await expect(firstPage.getByRole('columnheader').first()).toHaveText(/external_value\s*INTEGER/);
  await expect(secondPage.getByRole('tab', { name: 'External View', exact: true })).toHaveAttribute('aria-selected', 'true', { timeout: 12_000 });
}

async function renameAndRestoreView(page: Page) {
  const view = page.getByRole('tab', { name: 'View 1', exact: true });
  await view.dblclick();
  const renameDialog = page.getByRole('dialog', { name: 'View name' });
  const title = renameDialog.getByRole('textbox');
  await expect(title).toHaveValue('View 1');
  await renameDialog.getByRole('button', { name: 'Cancel' }).click();
  await expect(view).toBeVisible();
  await view.dblclick();
  await page.keyboard.press('Escape');
  await expect(renameDialog).toHaveCount(0);
  await expect(view).toBeVisible();
  await page.keyboard.press('Meta+P');
  const palette = page.getByRole('dialog', { name: 'Command palette' });
  const paletteInput = palette.getByRole('textbox');
  await paletteInput.fill('Rename View');
  await expect(palette.getByRole('button', { name: 'Rename View', exact: true })).toBeEnabled();
  await paletteInput.press('Enter');
  await expect(title).toHaveValue('View 1');
  await expect(title).toBeFocused();
  await title.fill('E2E View');
  await title.press('Enter');
  await replaceSql(page, "SELECT 'saved worksheet'");
  await page.waitForTimeout(5200);
  const restored = await page.context().newPage();
  await restored.goto(url);
  await expect(restored.getByRole('tab', { name: /E2E View/ })).toBeVisible();
  await expect(editor(restored)).toContainText("SELECT 'saved worksheet'");
  await restored.close();
}

async function verifyEmbeddedDensity(browser: Browser) {
  const embedded = await browser.newContext();
  const embeddedPage = await embedded.newPage();
  try {
    const embeddedUrl = new URL(url); embeddedUrl.searchParams.set('embedded', '1');
    await embeddedPage.goto(embeddedUrl.toString());
    await expect.poll(() => embeddedPage.evaluate(() => document.documentElement.dataset.density)).toBe('compact');
  } finally { await embedded.close(); }
}


export { url, editor, projectName, replaceSql, runSql, sharedWorkspace, persistedAdaptiveWorkspace, openSharedPages, renameAndRestoreView, verifyEmbeddedDensity };
