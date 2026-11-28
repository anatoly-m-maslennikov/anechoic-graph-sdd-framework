
import { expect, test, type Page } from '@playwright/test';
import { replaceSql } from '../unit/support/support__shared';
import { mockGraph } from '../unit/support/support__shared';
import { isToolCall, matchesToolPath, toolReply,
  toolRequest } from '../unit/support/support__shared';

test('browser fetches inline rows while MCP defaults to files',
  async ({ page }) => {
  const url = new URL(process.env.WORKBENCH_E2E_URL!);
  const fetched: Record<string, unknown>[] = [];
  page.on('request', request => {
    if (!isToolCall(request)) return;
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
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
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
      await page.route(matchesToolPath, async route => {
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

for (const queryId of [undefined, 'run-1']) {
  test(`a saved query keeps the ${queryId ? 'mismatched' : 'missing'} result refusal`,
    async ({ page }) => {
    await mockGraph(page, 'table', 'vertical', 'SELECT 1');
    let submitted = false;
    await page.route(matchesToolPath, async route => {
      if (route.request().method() !== 'POST') return route.fallback();
      const { name } = toolRequest(route);
      if (name === 'view_run') {
        submitted = true;
        return route.fulfill({ json: toolReply(route, {
          status: 'success', revision: 1, query_id: queryId,
          saved_query_id: 'saved-1', saved_query_url: '/saved/saved-1',
        }) });
      }
      if (submitted && name === 'view_fetch') return route.fulfill({ json: toolReply(route, {
        query_id: 'run-2', columns: [], rows: [],
      }) });
      return route.fallback();
    });
    await page.goto(process.env.WORKBENCH_E2E_URL!);
    await expect(page.getByRole('grid')).toBeVisible();
    await page.getByRole('button', { name: 'Run & Save' }).click();
    await page.getByRole('dialog', { name: 'Bookmark name' })
      .getByRole('button', { name: 'Save', exact: true }).click();
    await expect(page.getByRole('alert').filter({ hasText: queryId
      ? 'The View result changed before it could be displayed.'
      : 'The completed query has no result ID.' })).toBeVisible();
    await expect(page.locator('.saved-reference')).toHaveCount(1);
    await expect(page.getByRole('grid')).toHaveCount(0);
  });
}

async function mockPages(page: Page) {
  await mockGraph(page, 'table', 'vertical', 'SELECT 1');
  let release!: () => void;
  let started!: () => void;
  const held = new Promise<void>(resolve => { release = resolve; });
  const pending = new Promise<void>(resolve => { started = resolve; });
  let pages = 0;
  await page.route(matchesToolPath, async route => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    if (name !== 'view_fetch') return route.fallback();
    const offset = Number(args.offset || 0);
    if (offset && ++pages === 2) { started(); await held; }
    const value = offset ? (pages === 1 ? 'wrong' : 'new') : 'old';
    return route.fulfill({ json: toolReply(route, {
      query_id: value === 'wrong' ? 'other' : 'q1',
      columns: [{ name: 'value', type: 'VARCHAR' }], rows: [[value]],
      row_count: 2, column_count: 1, offset, page_size: 1,
      has_more: offset === 0,
    }) });
  });
  return { release, pending };
}

test('paging refuses another query and preserves a pending format error',
  async ({ page }) => {
  const { release, pending } = await mockPages(page);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  const grid = page.getByRole('grid');
  await expect(grid).toContainText('old');
  await page.getByRole('tab', { name: 'Settings', exact: true }).click();
  await page.getByRole('radio', { name: 'Fixed' }).check();
  await page.getByRole('tab', { name: 'Graph', exact: true }).click();
  await expect(grid).toContainText('old');
  const next = page.getByRole('navigation', { name: 'Result pages' })
    .getByRole('button', { name: 'Next' });
  const first = page.waitForResponse(response => isToolCall(response.request()) &&
    response.request().postDataJSON()?.name === 'view_fetch' &&
    response.request().postDataJSON()?.arguments?.offset > 0);
  await next.click();
  await (await first).finished();
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(
    () => requestAnimationFrame(resolve))));
  await expect(grid).toContainText('old');
  await expect(grid).not.toContainText('wrong');
  await next.click();
  await pending;
  await replaceSql(page, 'select [');
  await page.getByRole('button', { name: 'Format', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText(/Parse error/);
  release();
  await expect(grid).toContainText('new');
  await expect(page.getByRole('alert')).toContainText(/Parse error/);
  await expect(page.getByRole('textbox', { name: 'Query editor' }))
    .toContainText('select [');
});
