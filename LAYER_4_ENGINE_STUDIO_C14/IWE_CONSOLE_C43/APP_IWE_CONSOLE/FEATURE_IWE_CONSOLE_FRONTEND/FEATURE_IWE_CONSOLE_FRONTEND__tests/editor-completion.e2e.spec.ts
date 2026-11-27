
import { expect, test, type Page } from '@playwright/test';
import { isToolCall, matchesToolPath, toolRequest } from './tool_rest_fixture';

const url = process.env.WORKBENCH_E2E_URL!;
const editor = (page: Page) => page.getByRole(
  'textbox', { name: 'Query editor' });

async function typeQuery(page: Page, sql: string) {
  await editor(page).click();
  await editor(page).press('ControlOrMeta+A');
  await editor(page).pressSequentially(sql);
  await expect(editor(page)).toHaveText(sql);
}

async function moveBefore(page: Page, suffix: string) {
  for (let index = 0; index < suffix.length;
    index += 1) await page.keyboard.press('ArrowLeft');
}

async function verifyColumnCompletions(page: Page) {
  for (const qualifier of ['atoms', 'a']) {
    const suffix = qualifier === 'a' ? ' FROM atoms AS a' : '';
    await typeQuery(page, `SELECT ${qualifier}.head${suffix}`);
    await moveBefore(page, suffix);
    await page.keyboard.press('Control+Space');
    await page.getByRole('option', { name:
      /header\.state\.status/ }).first().click();
    await expect(editor(page)).toHaveText(
      `SELECT ${qualifier}."header.state.status"${suffix}`);
  }

  await typeQuery(page, 'SELECT atoms."header.st"');
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name:
    /header\.state\.status/ }).first().click();
  await expect(editor(page)).toHaveText('SELECT atoms."header.state.status"');

  await typeQuery(page, 'SELECT header.st');
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name:
    /header\.state\.status/ }).first().click();
  await expect(editor(page)).toHaveText('SELECT "header.state.status"');

  for (const [qualifier, suffix] of [['"a"',
    ' FROM atoms AS "a"'], ['header', ' FROM atoms AS header']]) {
    await typeQuery(page, `SELECT ${qualifier}.head${suffix}`);
    await moveBefore(page, suffix);
    await page.keyboard.press('Control+Space');
    await page.getByRole('option', { name:
      /header\.state\.status/ }).first().click();
    await expect(editor(page)).toHaveText(
      `SELECT ${qualifier}."header.state.status"${suffix}`);
  }

  await typeQuery(page, 'SELECT atoms."header.state.status" FROM atoms');
  await moveBefore(page, 'ate.status" FROM atoms');
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name:
    /header\.state\.status/ }).first().click();
  await expect(editor(page)).toHaveText(
    'SELECT atoms."header.state.status" FROM atoms');

  await typeQuery(page, 'SELECT "header.state.status" FROM atoms');
  await moveBefore(page, 'ate.status" FROM atoms');
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name: /header\.state\.status/ }).first().click();
  await expect(editor(page)).toHaveText('SELECT "header.state.status" FROM atoms');

}

async function verifyStatusCompletions(page: Page) {
  await typeQuery(page,
    `SELECT * FROM atoms WHERE "header.state.status" = 'active'`);
  await moveBefore(page, `ive'`);
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name: 'active', exact: true }).click();
  await expect(editor(page)).toHaveText(
    `SELECT * FROM atoms WHERE "header.state.status" = 'active'`);

  await typeQuery(page,
    `SELECT * FROM atoms WHERE "header.state.status" = 'O''R'`);
  await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name: "O'Reilly", exact: true }).click();
  await expect(editor(page)).toHaveText(
    `SELECT * FROM atoms WHERE "header.state.status" = 'O''Reilly'`);
  await moveBefore(page, `eilly'`);
  await page.keyboard.press('Control+Space');
  await page.getByRole('option', { name: "O'Reilly", exact: true }).click();
  await expect(editor(page)).toHaveText(
    `SELECT * FROM atoms WHERE "header.state.status" = 'O''Reilly'`);
}

test('completes qualified columns and escapes Status values without executing SQL',
  async ({ page }) => {
  const operations: string[] = [];
  page.on('request', (request) => {
    if (isToolCall(request)) operations.push(request.postDataJSON()?.name);
  });
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    if (toolRequest(route)?.name !== 'query_schema') return route.fallback();
    const response = await route.fetch();
    const envelope = await response.json();
    const schema = envelope.result.value;
    const status = schema.tables.atoms.find((column: { name:
      string }) => column.name === 'header.state.status');
    expect(status).toBeTruthy();
    status.values = [...(status.values ?? []), "O'Reilly"];
    await route.fulfill({ response, json: envelope });
  });
  const schemaReady = page.waitForResponse(response =>
    isToolCall(response.request()) && response.ok() &&
    response.request().postDataJSON()?.name === 'query_schema');
  await page.goto(url);
  await (await schemaReady).finished();
  await page.evaluate(() => new Promise<void>(
    resolve => requestAnimationFrame(() => resolve())));
  await expect(editor(page)).toBeEditable();

  await verifyColumnCompletions(page);
  await verifyStatusCompletions(page);
  expect(operations.filter((operation) =>
    /^(?:view_run|view_check|query_run|query_check|view_save)$/.test(
      operation))).toEqual([]);
});
