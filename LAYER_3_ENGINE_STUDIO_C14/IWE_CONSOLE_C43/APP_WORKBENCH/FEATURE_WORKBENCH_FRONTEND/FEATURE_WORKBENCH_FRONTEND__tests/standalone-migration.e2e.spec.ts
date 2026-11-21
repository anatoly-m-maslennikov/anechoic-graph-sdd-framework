// CA-E-781@2
import { expect, test, type Page } from '@playwright/test';

const url = process.env.WORKBENCH_E2E_URL!;
const editor = (page: Page) => page.getByRole('textbox', { name: 'Query editor' });
const projectName = new URL(url).pathname.split('/').filter(Boolean).at(-1)!;

async function replaceSql(page: Page, sql: string) {
  const input = editor(page);
  await expect(input).toBeEditable();
  await expect(input).toHaveAttribute('contenteditable', 'true');
  await input.click();
  await input.press('Meta+A');
  await input.pressSequentially(sql);
  await expect(input).toContainText(sql);
}
test('migrates one standalone draft without running it and keeps close protection after sync', async ({ browser }) => {
  const context = await browser.newContext(); const page = await context.newPage();
  const parsed = new URL(url); const root = parsed.searchParams.get('project_root') ?? projectName;
  const legacyKey = `anechoic.workbench.${root}.workspace`;
  await page.addInitScript(({ key }) => localStorage.setItem(key, JSON.stringify({ activeId: 'legacy', tabs: [{ id: 'legacy', title: 'View 1', sql: 'SELECT 41 AS migrated_draft', cursor: 0, dirty: true, savedSql: '' }] })), { key: legacyKey });
  let runs = 0; const opened: string[] = [];
  page.on('request', (request) => {
    if (request.method() !== 'POST' || !new URL(request.url()).pathname.endsWith('/interface')) return;
    const payload = request.postDataJSON(); if (payload?.operation === 'view_run') runs += 1;
    if (payload?.operation === 'workspace_open') opened.push(payload.arguments?.session_id);
  });
  try {
    await page.goto(url);
    await expect(editor(page)).toContainText('SELECT 41 AS migrated_draft');
    expect(new URL(page.url()).searchParams.get('workspace')).toBeNull();
    const session = await page.evaluate(() => Object.entries(localStorage).find(([key]) => key.endsWith('.standalone-session'))?.[1]);
    expect(session).toMatch(/^standalone-/); expect(opened).toEqual([session]); expect(runs).toBe(0);
    await page.reload(); await expect(editor(page)).toContainText('SELECT 41 AS migrated_draft');
    expect(new URL(page.url()).searchParams.get('workspace')).toBeNull(); await expect.poll(() => opened).toEqual([session, session]);

    const update = page.waitForRequest((request) => request.method() === 'POST' && new URL(request.url()).pathname.endsWith('/interface') && request.postDataJSON()?.operation === 'view_update' && request.postDataJSON()?.arguments?.sql === 'SELECT 42 AS autosaved_draft');
    await replaceSql(page, 'SELECT 42 AS autosaved_draft'); await update;
    const close = page.locator('button[aria-label^="Close "]').first();
    let message = ''; page.once('dialog', (dialog) => { message = dialog.message(); void dialog.dismiss(); });
    await close.click(); expect(message).toContain('Close unsaved');
    await expect(editor(page)).toContainText('SELECT 42 AS autosaved_draft'); expect(runs).toBe(0);
  } finally { await context.close(); }
});

test('resumes a partial standalone migration without overwriting existing Views or duplicate acknowledgements', async ({ browser }) => {
  const context = await browser.newContext(); const page = await context.newPage(); const workspace = `standalone-existing-${Date.now()}`;
  const parsed = new URL(url); const endpoint = new URL(`${parsed.pathname.replace(/\/$/, '')}/interface`, parsed.origin).toString(); const root = parsed.searchParams.get('project_root') ?? projectName;
  const call = async (operation: string, arguments_: Record<string, unknown>) => {
    const response = await fetch(endpoint, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ operation, arguments: arguments_, ...(parsed.searchParams.get('project_root') ? { project_root: parsed.searchParams.get('project_root') } : {}) }) });
    expect(response.ok, `${operation} failed`).toBeTruthy(); return response.json() as Promise<Record<string, any>>;
  };
  const opened = await call('workspace_open', { session_id: workspace }); const initial = opened.views[0];
  await call('view_update', { workspace_id: workspace, view_id: initial.id, sql: 'SELECT 7 AS existing_view', expected_revision: initial.revision, cursor_position: 0 });
  const legacyKey = `anechoic.workbench.${root}.workspace`; const sessionKey = `anechoic.workbench.${root}.standalone-session`;
  const legacy = JSON.stringify({ activeId: 'second', tabs: [
    { id: 'first', title: 'View 1', sql: 'SELECT 8 AS imported_once', cursor: 0, dirty: true, savedSql: '' },
    { id: 'second', title: 'View 2', sql: 'SELECT 9 AS resumed_import', cursor: 0, dirty: true, savedSql: '' },
  ] });
  await page.addInitScript(({ draftKey, sessionKey: key, session, draft }) => { localStorage.setItem(key, session); localStorage.setItem(draftKey, draft); }, { draftKey: legacyKey, sessionKey, session: workspace, draft: legacy });
  let failSecond = true;
  await page.route('**/interface', async (route) => {
    const request = route.request().postDataJSON() as { operation?: string; arguments?: { sql?: string } };
    if (failSecond && request.operation === 'view_update' && request.arguments?.sql === 'SELECT 9 AS resumed_import') return route.fulfill({ status: 500, contentType: 'application/json', body: '{"error":"temporary import failure"}' });
    await route.continue();
  });
  try {
    await page.goto(url); await expect(page.getByRole('alert')).toContainText('temporary import failure');
    let state = await call('workspace_get', { workspace_id: workspace });
    expect(state.views.filter((item: { sql: string }) => item.sql === 'SELECT 7 AS existing_view')).toHaveLength(1);
    expect(state.views.filter((item: { sql: string }) => item.sql === 'SELECT 8 AS imported_once')).toHaveLength(1);
    failSecond = false; await page.reload(); await expect(editor(page)).toContainText('SELECT 9 AS resumed_import');
    state = await call('workspace_get', { workspace_id: workspace });
    expect(state.views.filter((item: { sql: string }) => item.sql === 'SELECT 7 AS existing_view')).toHaveLength(1);
    expect(state.views.filter((item: { sql: string }) => item.sql === 'SELECT 8 AS imported_once')).toHaveLength(1);
    expect(state.views.filter((item: { sql: string }) => item.sql === 'SELECT 9 AS resumed_import')).toHaveLength(1);
    expect(state.views).toHaveLength(3);
    await expect.poll(() => page.evaluate((key) => localStorage.getItem(key), legacyKey)).toBe(legacy);
  } finally { await context.close(); }
});

