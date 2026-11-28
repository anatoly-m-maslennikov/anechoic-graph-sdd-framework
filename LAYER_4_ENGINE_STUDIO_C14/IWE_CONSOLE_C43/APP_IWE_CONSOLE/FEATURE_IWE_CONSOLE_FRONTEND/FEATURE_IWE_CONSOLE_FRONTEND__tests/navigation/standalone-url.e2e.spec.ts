import { expect, test, type Page, type Request } from '@playwright/test';
import { replaceSql } from '../unit/support/support__shared';
import { formalCases } from '../unit/support/support__shared';
import { browserTimeout } from '../unit/support/support__shared';
import { isToolCall, matchesToolPath, toolRequest } from '../unit/support/support__shared';

const url = process.env.WORKBENCH_E2E_URL!;

function isToolRequest(request: Request, name: string) {
  return isToolCall(request) &&
    request.postDataJSON()?.name === name;
}

type DiagnosticsCase = {
  name: string;
  input: { reply?: string; target?: string };
  effect: [string, string, { runtime?: string; message?: string }];
};

test('runs both formal Diagnostics rebuilds against the Project runtime',
  async ({ page }) => {
  const { inspect_console_diagnostics: cases } =
    formalCases<DiagnosticsCase>('inspect_console_diagnostics');
  const healthy = cases.find(item => item.name === 'healthy')!.effect[2].runtime!;
  const rebuilds = cases.filter(item => item.input.reply === 'success');
  expect(rebuilds.map(item => item.input.target)).toEqual(
    ['realization_graph', 'all']);
  await page.goto(url);
  await page.getByRole('tab', { name: 'Diagnostics', exact: true }).click();
  const panel = page.getByRole('region', { name: 'Diagnostics' });
  await expect(panel.getByText(healthy, { exact: true })).toBeVisible();
  for (const { input: { target }, effect: [, , { message }] } of rebuilds) {
    const replied = page.waitForResponse(reply =>
      isToolRequest(reply.request(), 'query_rebuild') &&
      reply.request().postDataJSON()?.arguments?.target === target);
    const name = target === 'all' ?
      'Rebuild Project database from source' : 'Rebuild Realization Graph';
    await panel.getByRole('button', { name, exact: true }).click();
    const response = await replied;
    const envelope = await response.json();
    expect(response.ok(), JSON.stringify(envelope)).toBeTruthy();
    const result = envelope.result?.value;
    expect(result).toMatchObject({ status: 'ready', target });
    await expect(panel.getByRole('status')).toHaveText(message!);
  }
});

test('opens a Document and restores authored SQL with a commented View directive',
  async ({ page }) => {
  const sql = 'SELECT reference FROM atoms WHERE "header.context.template" = \'project_manifest\' '
    + 'AND status_group = \'Current\' LIMIT 1 VIEW /* display */ DOCUMENT -- keep';
  await page.goto(url);
  const editor = page.getByRole('textbox', { name: 'Query editor' });
  await expect(editor).toBeEditable();
  await editor.fill(sql);
  await page.getByRole('button', { name: 'Run Cmd+Enter', exact: true }).click();
  await expect(page.locator('.document-stack').getByRole('article')).toBeVisible();
  await page.getByRole('button', { name: 'Save View', exact: true }).click();
  const saved = page.locator('.saved-reference').getByRole('link');
  await expect(saved).toHaveAttribute('href', /[?&]query=/);
  await page.goto((await saved.getAttribute('href'))!);
  await expect(editor).toHaveText(sql);
  await expect(page.getByRole('combobox', { name:
    'View', exact: true })).toHaveValue('document');
});

async function runWithTerminalDiagnostics(page: Page) {
  const error = page.locator('.editor-panel p.error[role="alert"]').first();
  const uiFailure = error.waitFor({ state: 'visible', timeout: 0 }).then(async () => {
    throw new Error(`Workbench query failed: ${await error.innerText()}`);
  });
  const response = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'view_run'), { timeout: 0 });
  const terminal = Promise.race([response, uiFailure]);
  const [reply] = await Promise.all([terminal, page.getByRole(
    'button', { name: 'Run Cmd+Enter' }).click()]);
  const body = await reply.text();
  expect(reply.ok(), `Workbench view_run HTTP ${reply.status(
    )}: ${body}`).toBeTruthy();
  const value = JSON.parse(body).result?.value;
  expect(value?.status, `Workbench view_run failed: ${body}`).toBe('success');
  await Promise.race([expect(page.getByRole(
    'columnheader')).toHaveText(/in_memory/), uiFailure]);
}

async function openWorkspace(page: Page, sessionId: string) {
  const workbench = new URL(url);
  const endpoint = new URL(`${workbench.pathname.replace(
    /\/$/, '')}/interface`, workbench.origin);
  const response = await page.request.post(endpoint.toString(), { data: {
    operation: 'workspace_open', arguments: { session_id: sessionId } } });
  const body = await response.text(); expect(response.ok(), body).toBeTruthy();
  return JSON.parse(body) as { project_root: string };
}

test('cleans only this browser legacy standalone URL and preserves explicit Workspace links',
  async ({ browser }) => {
  const context = await browser.newContext(); const page = await context.newPage();
  const ownId = `standalone-url-own-${Date.now()}`;
    const foreignId = `chat-workspace-${Date.now()}`;
  try {
    const own = await openWorkspace(page, ownId);
      await openWorkspace(page, foreignId);
    const sessionKey = `anechoic.workbench.${own.project_root}.standalone-session`;
    await page.addInitScript(({ key, value }) => localStorage.setItem(
      key, value), { key: sessionKey, value: ownId });

    const legacy = new URL(url);
    legacy.searchParams.set('workspace', ownId);
      legacy.searchParams.set('project_root', own.project_root);
    legacy.searchParams.set('query', ''); legacy.searchParams.set(
      'keep', 'value'); legacy.hash = 'standalone-fragment';
    const clean = new URL(legacy); clean.searchParams.delete('workspace');
    await page.goto(legacy.toString()); await expect(page.getByRole(
      'button', { name: 'Run Cmd+Enter' })).toBeEnabled();
    expect(page.url()).toBe(clean.toString());
    await page.reload(); await expect(page.getByRole(
      'button', { name: 'Run Cmd+Enter' })).toBeEnabled();
    expect(page.url()).toBe(clean.toString());

    const foreign = new URL(clean);
    foreign.searchParams.set('workspace', foreignId);
      foreign.searchParams.set('chat', '1'); foreign.hash = 'chat-fragment';
    await page.goto(foreign.toString()); await expect(page.getByRole(
      'button', { name: 'Run Cmd+Enter' })).toBeEnabled();
    expect(page.url()).toBe(foreign.toString());

    const embedded = new URL(clean);
    embedded.searchParams.set('workspace', ownId); embedded.searchParams.set(
      'embedded', '1'); embedded.hash = 'embedded-fragment';
    const embeddedClean = new URL(embedded);
      embeddedClean.searchParams.delete('workspace');
    await page.goto(embedded.toString()); await expect(page.getByRole(
      'button', { name: 'Run Cmd+Enter' })).toBeEnabled();
    expect(page.url()).toBe(embeddedClean.toString());
    await expect(page.locator('html')).toHaveAttribute('data-density', 'compact');
    await page.reload(); await expect(page.getByRole(
      'button', { name: 'Run Cmd+Enter' })).toBeEnabled();
    expect(page.url()).toBe(embeddedClean.toString());
  } finally { await context.close(); }
});

for (const method of ['getItem', 'setItem']) {
  test(`keeps unsaved SQL usable when browser storage ${method} fails`,
    async ({ page }) => {
    await page.addInitScript((operation) => {
      Object.defineProperty(Storage.prototype, operation, {
        value() { throw new DOMException('Storage is unavailable', 'SecurityError'); },
      });
    }, method);
    await page.goto(url);
    const warning = page.getByRole('alert').filter({
      hasText: 'Browser storage is unavailable' });
    await expect(warning).toHaveText(
      'Browser storage is unavailable. Reloading or closing IWE Console may lose unsaved edits.');
    const editor = page.getByRole('textbox', { name: 'Query editor' });
    await replaceSql(page, 'SELECT 7 AS in_memory');
    await expect(editor).toHaveText('SELECT 7 AS in_memory');
    await runWithTerminalDiagnostics(page);
    await expect(editor).toHaveText('SELECT 7 AS in_memory');
    await expect(warning).toBeVisible();
  });
}

test('uses the canonical Project name and rejects a Workspace without it',
  async ({ page }) => {
  let omitName = false;
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    if (toolRequest(route)?.name !== 'workspace_open') return route.fallback();
    const response = await route.fetch();
    expect(response.ok(), await response.text()).toBeTruthy();
    const envelope = await response.json();
    const { project_name, ...rest } = envelope.result.value;
    expect(project_name).toEqual(expect.any(String));
    envelope.result.value = omitName ? rest :
      { ...rest, project_name: 'Canonical Project' };
    await route.fulfill({ response, json: envelope });
  });
  await page.goto(url);
  const run = page.getByRole('button', { name: 'Run Cmd+Enter' });
  await expect(run).toBeEnabled();
  await expect(page.locator('header')).toContainText('Project: Canonical Project');
  omitName = true;
  await page.reload();
  await expect(page.getByRole('alert')).toContainText(
    'Workspace binding requires the Project name.');
  await expect(run).toBeDisabled();
});


const initialLifecycleBody = '## Summary\n\nDisposable lifecycle Ticket\n';

async function createCurrentTicket(page: Page, publishStatus: string) {
  await page.getByText('Create Atom', { exact: true }).click();
  await page.getByPlaceholder('C00').fill('C00');
  await page.getByLabel('Body', { exact: true }).fill(initialLifecycleBody);
  const initialCreation = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'atom_lifecycle_create_draft'));
  await page.getByRole('button', { name: 'Create Draft' }).click();
  const initialResponse = await initialCreation;
  const initialEnvelope = await initialResponse.json();
  const initialResult = initialEnvelope.result?.value;
  expect(initialResponse.ok(), JSON.stringify(initialEnvelope)).toBeTruthy();
  expect(initialResult?.status, JSON.stringify(initialEnvelope)).toBe('completed');
  const initialDraft = initialResult.savedDraft.ref_id as string;
  const stable = initialDraft.split('@')[0];
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await expect(dialog).toContainText(initialDraft);
  await dialog.getByRole('combobox', { name: 'Status' }).selectOption(publishStatus);
  const initialPromotion = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'atom_lifecycle_promote_draft'));
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  const initialPromoteResponse = await initialPromotion;
  const initialPromoteEnvelope = await initialPromoteResponse.json();
  expect(initialPromoteResponse.ok(), JSON.stringify(
    initialPromoteEnvelope)).toBeTruthy();
  expect(initialPromoteEnvelope.result?.value?.status, JSON.stringify(
    initialPromoteEnvelope)).toBe('completed');
  await expect(dialog.getByRole('button', { name: 'Edit Draft' })).toBeVisible();
  await dialog.getByRole('button', { name: 'Close', exact: true }).click();
  return stable;
}

async function reopenDraft(page: Page, stable: string) {
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  const created = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'atom_lifecycle_create_draft'));
  await dialog.getByRole('button', { name: 'Edit Draft' }).click();
  const createResponse = await created;
  expect(createResponse.ok()).toBeTruthy();
  const createEnvelope = await createResponse.json();
  const createResult = createEnvelope.result?.value;
  expect(createResult?.status, JSON.stringify(createEnvelope)).toBe('completed');
  const draft = createResult.savedDraft.ref_id as string;
  await expect(dialog).toContainText(draft);
  await dialog.getByRole('button', { name: 'Close', exact: true }).click();
  let additionalCreations = 0;
  page.on('request', request => {
    if (isToolRequest(request, 'atom_lifecycle_create_draft')) additionalCreations++;
  });
  await page.getByRole('grid').getByRole('button',
    { name: stable, exact: true }).click();
  await dialog.getByRole('button', { name: 'Edit Draft' }).click();
  await expect(dialog).toContainText(draft);
  expect(additionalCreations).toBe(0);
}

async function expectSummaryRefusal(page: Page, message: string) {
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  const editor = dialog.getByLabel('Body', { exact: true });
  const changedSummary = initialLifecycleBody.replace('Disposable', 'Renamed');
  let promotions = 0;
  const onRequest = (request: Request) => {
    if (isToolRequest(request, 'atom_lifecycle_promote_draft')) promotions++;
  };
  page.on('request', onRequest);
  try {
    await editor.fill(changedSummary);
    await dialog.getByRole('button', { name: 'Promote Draft' }).click();
    await expect(dialog.getByRole('alert')).toHaveText(message);
    await expect(editor).toHaveValue(changedSummary);
    await expect(dialog.getByText('Unsaved changes', { exact: true })).toBeVisible();
    expect(promotions).toBe(0);
  } finally {
    page.off('request', onRequest);
  }
}

test('edits and promotes an existing Ticket in disposable Studio',
  async ({ page }) => {
  test.skip(process.env.WORKBENCH_LIFECYCLE_E2E !== '1', 'Requires a disposable test Project');
  const endpoint = new URL(url);
  expect(endpoint.hostname).toBe('127.0.0.1');
  type LifecycleCase = { input: { operation: string; family: string }; effect: [string, string, {
    publish_status?: string; reopens_existing?: boolean;
      autosave_seconds?: number; summary_error?: string;
  }] };
  const cases = formalCases<LifecycleCase>('observe_atom_lifecycle').observe_atom_lifecycle;
  const task = cases.find(item => item.input.operation === 'task_edit' && item.input.family === 'T')!;
  expect(task.effect.slice(0, 2)).toEqual(['C46.lifecycle_observation', 'observed']);
  const expected = task.effect[2];
  expect(expected.reopens_existing).toBe(true);
  await page.goto(url);
  const stable = await createCurrentTicket(page, expected.publish_status!);
  await replaceSql(page, `SELECT reference FROM atoms WHERE reference = '${stable}' AND status_group = 'Current'`);
  await page.getByRole('button', { name: 'Run Cmd+Enter' }).click();
  const link = page.getByRole('grid').getByRole('button', { name: stable, exact: true });
  await link.click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await reopenDraft(page, stable);
  await expectSummaryRefusal(page, expected.summary_error!);
  const body = initialLifecycleBody + '\nUpdated in disposable Studio\n';
  const saved = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'atom_lifecycle_update'),
    { timeout: browserTimeout((expected.autosave_seconds! + 15) * 1000) });
  await dialog.getByLabel('Body', { exact: true }).fill(body);
  const saveResponse = await saved;
  expect(saveResponse.ok()).toBeTruthy();
  const saveEnvelope = await saveResponse.json();
  expect(saveEnvelope.result?.value?.status, JSON.stringify(saveEnvelope)).toBe('completed');
  await expect(dialog.getByText('Saved', { exact: true })).toBeVisible();
  await dialog.getByRole('combobox', { name: 'Status' }).selectOption(expected.publish_status!);
  const promoted = page.waitForResponse(reply =>
    isToolRequest(reply.request(), 'atom_lifecycle_promote_draft'));
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  const promoteResponse = await promoted;
  expect(promoteResponse.request().postDataJSON(
    ).arguments.targetStatus).toBe(expected.publish_status);
  expect(promoteResponse.ok()).toBeTruthy();
  const promoteEnvelope = await promoteResponse.json();
  expect(promoteEnvelope.result?.value?.status, JSON.stringify(promoteEnvelope)).toBe('completed');
  await expect(dialog.getByRole('button', { name: 'Edit Draft' })).toBeVisible();
  await expect(dialog.locator('.atom-document .body')).toHaveText(body);
});
