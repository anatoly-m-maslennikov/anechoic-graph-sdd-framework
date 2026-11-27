import { expect, test, type Page } from '@playwright/test';
import { checkObservedEffects, checkObservedValues, formalCases,
  type CorrelatedCase } from './console-formal-cases';
import { lifecycleFixture, observeLifecycle, watchAppearance,
  watchDraft } from './console-lifecycle-fixture';

type Detail = { operation?: string; family?: string;
  template?: string; tier?: number; lens?: string;
  target_status?: string; autosave_seconds?: number; removed_type?
    : string; removed_ref?: string; authored_only?: boolean;
  publish_status?: string; current_status?: string;
    reopens_existing?: boolean; component?: string; error?: string;
  current_body?: string; ticket_statuses?: string[] };
type Case = CorrelatedCase & { input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>('observe_atom_lifecycle', 'guard_draft_editor');

async function taskEdit(page: Page, input: Detail, expected: Detail) {
  const { calls, exact } = await lifecycleFixture(page, input.family);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByText('Create Atom', { exact: true }).click();
  await page.getByPlaceholder('C00').fill('C00');
  await page.getByLabel('Body', { exact: true }).first().fill('## Summary\n\nCreated\n');
  await page.getByRole('button', { name: 'Create Draft' }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await expect(dialog).toContainText(exact);
  const editor = dialog.getByLabel('Body', { exact: true });
  await expect(dialog.getByRole('region', { name: 'Atom lifecycle' })
    .getByRole('button', { name: expected.removed_ref, exact: true })).toBeVisible();
  await expect(dialog.getByRole('button', { name: 'C00', exact: true })).toHaveCount(0);
  await editor.fill('## Summary\n\nCreated\n\nEdited\n');
  await dialog.getByRole('button', { name: `Remove ${expected.removed_type} ${expected.removed_ref}` }).click();
  if (expected.authored_only) {
    await expect(dialog.getByRole('button', { name: /Remove (?:DERIVED|INCOMING|CONTAINED_BY)/ })).toHaveCount(0);
  }
  await page.waitForTimeout((expected.autosave_seconds! - 1) * 1000);
  expect(calls.filter((c) => c.operation === 'atom_lifecycle_update')).toHaveLength(0);
  await expect.poll(() => calls.filter((c) =>
    c.operation === 'atom_lifecycle_update').length, { timeout: 8000 }).toBe(1);
  const update = calls.find((c) => c.operation === 'atom_lifecycle_update')!.arguments;
  expect(update).toEqual({ target: { ref_id: exact, version: 1 }, expectedUpdatedAt: 'one',
    changes: { body: '## Summary\n\nCreated\n\nEdited\n', removeRelations:
      [{ type: expected.removed_type, ref_id: expected.removed_ref }] } });
  await expect(dialog.getByText('Saved', { exact: true })).toBeVisible();
  await editor.fill('## Summary\n\nCreated\n\nFinal edit\n');
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  await expect.poll(() => calls.some(call => call.operation === 'atom_lifecycle_promote_draft')).toBe(true);
  expect(calls.find((c) => c.operation === 'atom_lifecycle_promote_draft')?.arguments.targetStatus).toBe(expected.publish_status);
  const mutations = calls.filter((c) => ['atom_lifecycle_update',
    'atom_lifecycle_promote_draft'].includes(c.operation));
  expect(mutations.map((c) => c.operation)).toEqual(['atom_lifecycle_update',
    'atom_lifecycle_update', 'atom_lifecycle_promote_draft']);
  expect(mutations[1].arguments).toMatchObject({ expectedUpdatedAt:
    'two', changes: { body: '## Summary\n\nCreated\n\nFinal edit\n' } });
  await expect(dialog.getByRole('button', { name: 'Edit Draft' })).toBeVisible();
  await dialog.getByRole('button', { name: 'Change status' }).click();
  await expect.poll(() => calls.some((c) => c.operation === 'atom_lifecycle_change_status')).toBe(true);
  expect(calls.find((c) => c.operation === 'atom_lifecycle_change_status')?.arguments.targetStatus).toBe(expected.current_status);
  await dialog.getByRole('button', { name: 'Edit Draft' }).click();
  await expect(dialog.getByRole('button', { name: 'Promote Draft' })).toBeVisible();
  expect(calls.filter((c) => c.operation === 'atom_lifecycle_create_draft')).toHaveLength(expected.reopens_existing ? 1 : 2);
}

async function principleCreate(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page,
    'S', false, undefined, { refuseCreate: true });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByText('Create Atom', { exact: true }).click();
  await page.locator('form').getByLabel(
    'Template').selectOption(input.template!);
  await page.locator('form').getByLabel('Tier').selectOption(String(input.tier));
  await page.locator('form').getByLabel('Lens').fill(input.lens!);
  await page.getByLabel('Body', { exact:
    true }).fill('## Summary\n\nPrinciple\n');
  await page.getByRole('button', { name: 'Create Draft' }).click();
  await expect(page.getByRole('alert')).toContainText(expected.error!);
  expect(calls.find(call =>
    call.operation === 'atom_lifecycle_create_draft')?.arguments).toEqual({
    newAtom: { template: expected.template, container: { component: expected.component },
      lens: expected.lens, tier: expected.tier, body: '## Summary\n\nPrinciple\n' } });
}

async function specActivate(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page, input.family);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByText('Create Atom', { exact: true }).click();
  await page.locator('form').getByLabel(
    'Template').selectOption(input.template!);
  await page.getByLabel('Body', { exact:
    true }).first().fill('## Summary\n\nCreated\n');
  await page.getByRole('button', { name: 'Create Draft' }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await dialog.getByLabel('Body', { exact: true }).fill(expected.current_body!);
  await dialog.getByRole('combobox', { name:
    'Status' }).selectOption(input.target_status!);
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  await expect(dialog.getByText('AN-S-1 · active')).toBeVisible();
  await expect(dialog.locator(
    '.atom-document .body')).toHaveText(expected.current_body!);
  const writes = calls.filter((entry) => entry.operation.includes(
    'promote_draft') || entry.operation.includes('change_status'));
  expect(writes.map((entry) => [entry.operation,
    entry.arguments.targetStatus])).toEqual([
    ['atom_lifecycle_promote_draft', expected.publish_status],
    ['atom_lifecycle_change_status', expected.current_status],
  ]);
}

async function currentDraft(page: Page, scenario: Case, highestVersion: number) {
  const { calls, stable } = await lifecycleFixture(page,
    scenario.input.family, false, undefined, { highestVersion });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('grid').getByRole('button',
    { name: stable, exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  const edit = dialog.getByRole('button', { name: 'Edit Draft' });
  await expect(edit).toBeVisible();
  const effects = await observeLifecycle(page);
  await watchAppearance(page,
    'dialog[aria-label="Atom document"] .atom-document textarea',
    ['C46.lifecycle_observation', 'observed']);
  await edit.click();
  await expect(dialog.getByRole('button', {
    name: 'Promote Draft' })).toBeVisible();
  checkObservedEffects(scenario, await effects());
  const relevant = calls.filter(call => ['iwe_console_atom_document',
    'atom_lifecycle_create_draft'].includes(call.operation));
  expect(relevant.map(call => call.operation)).toEqual(['iwe_console_atom_document',
    'atom_lifecycle_create_draft', 'iwe_console_atom_document']);
  const [source, create, opened] = relevant;
  const returned = create.reply.savedDraft;
  expect(returned.ref_id).toBe(`${stable}@${highestVersion + 1}-draft`);
  const sourceFields = { source_ref: source.reply.ref_id,
    source_version: source.reply.version };
  const displayed = await dialog.locator(
    '.atom-document header > span .link').first().innerText();
  checkObservedValues(scenario, {
    current_draft: sourceFields, create_requested:
      create.arguments.sourceCurrent,
    draft_returned: returned, document_requested: opened.arguments,
    observed: { source_ref: create.arguments.sourceCurrent.ref_id, source_version:
      create.arguments.sourceCurrent.version, draft_ref: displayed },
  });
}

async function configuredStatus(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page,
    input.family, false, input.ticket_statuses);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('grid').getByRole('button',
    { name: 'AN-T-1', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  const statuses = dialog.getByRole('combobox', { name: 'Status' });
  await expect(statuses.locator('option')).toHaveText(
    ['In queue', 'Waiting review']);
  await statuses.selectOption(expected.current_status!);
  await dialog.getByRole('button', { name: 'Change status' }).click();
  await expect.poll(() => calls.find((call) =>
    call.operation === 'atom_lifecycle_change_status')?.arguments.targetStatus)
    .toBe(expected.current_status);
}

async function dirtyDraft(page: Page, refuseSave: boolean) {
  const fixture = await lifecycleFixture(page, 'T',
    true, undefined, { inline: true, refuseSave });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  const article = page.locator('.document-stack .atom-document');
  const ref = article.locator('header > span .link').first();
  const body = article.getByLabel('Body', { exact: true });
  const other = page.getByRole('tab', { name: 'Other View', exact: true });
  const calls = (operation: string) => fixture.calls.filter(
    call => call.operation === operation);
  const initial = '## Summary\n\nCreated\n';
  await body.fill(initial + '\nLocal changes\n');
  const source = calls('workspace_open')[0].reply;
  const dirty = { draft_ref: await ref.innerText(),
    changes: { body: await body.inputValue() } };
  const activeId = async () => {
    const title = await page.getByRole('tab', { selected: true }).innerText();
    return source.views.find((view: { name:
      string }) => view.name === title)?.id;
  };
  const effects = await observeLifecycle(page);
  await watchDraft(body);
  return { page, article, ref, body, other, initial,
    dirty, source, activeId, calls, fixture, effects };
}
type DirtyDraft = Awaited<ReturnType<typeof dirtyDraft>>;

async function renameInactive(scenario: Case, { page, article, body,
  other, dirty, source, activeId, calls, effects }: DirtyDraft) {
  const original = { view_id: source.views.find((view:
    { name: string }) => view.name === 'Other View').id,
    name: 'Renamed View', active_view_id: await activeId() };
  await watchAppearance(page, '[role="tab"]',
    ['C46.view', 'shown'], original.name);
  await other.click({ button: 'right' });
  await page.getByRole('menuitem', { name: 'Rename', exact: true }).click();
  const field = page.getByRole('dialog', {
    name: 'View name' }).getByRole('textbox');
  await field.fill(original.name); await field.press('Enter');
  await expect(page.getByRole('tab', { name:
    original.name, exact: true })).toBeVisible();
  checkObservedEffects(scenario, await effects());
  const [rename] = calls('view_rename');
  checkObservedValues(scenario, {
    rename_inactive: original, rename_requested:
      rename.arguments, rename_returned: rename.reply,
    view_observed: { active_view_id: await activeId() },
  });
  expect(calls('view_focus').some(call =>
    call.arguments.view_id === original.view_id)).toBe(false);
  await expect(body).toHaveValue(dirty.changes.body);
  await article.getByRole('button', { name: 'Save now' }).click();
  await expect(article.getByText('Saved', { exact: true })).toBeVisible();
  expect(calls('atom_lifecycle_update')[0].arguments).toMatchObject(
    { target: { ref_id: dirty.draft_ref }, changes: dirty.changes });
}

async function discardEdits(scenario: Case, { article, ref,
  body, other, initial, dirty, calls, effects }: DirtyDraft) {
  const confirmed = { draft_ref: await ref.innerText(
    ), changes: { body: await body.inputValue() } };
  await article.getByRole('button', { name:
    'Discard changes and reload' }).click();
  await expect(body).toHaveValue(initial);
  const reloaded = calls('iwe_console_atom_document').at(-1)!.arguments.ref_id;
  await other.click();
  await expect(body).toHaveCount(0);
  checkObservedEffects(scenario, await effects());
  expect(calls('atom_lifecycle_update')).toHaveLength(0);
  checkObservedValues(scenario, { leave_dirty: dirty, discard_confirmed:
    confirmed, editor_unmounted: { draft_ref: reloaded } });
}

async function saveEdits(scenario: Case, { ref, body,
  other, dirty, calls, fixture, effects }: DirtyDraft) {
  const departing = await ref.innerText();
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'true');
  await expect(body).toHaveCount(0);
  checkObservedEffects(scenario, await effects());
  const [save] = calls('atom_lifecycle_update');
  const relevant = fixture.calls.filter(call => [
    'atom_lifecycle_update', 'view_focus'].includes(call.operation));
  expect(relevant.map(call => call.operation)).toEqual(
    ['atom_lifecycle_update', 'view_focus']);
  checkObservedValues(scenario, {
    leave_dirty: dirty, save_requested: {
      ...save.arguments.target, changes: save.arguments.changes },
    save_succeeded: save.reply.artifact,
      editor_unmounted: { draft_ref: departing },
  });
}

async function refuseEdits(scenario: Case, { article, ref,
  body, other, initial, dirty, calls, effects }: DirtyDraft) {
  await other.click();
  await expect(article.getByRole('alert')).toHaveText(
    'Draft updated_at does not match the expected timestamp.');
  checkObservedEffects(scenario, await effects());
  const [save] = calls('atom_lifecycle_update');
  checkObservedValues(scenario, {
    leave_dirty: dirty, save_requested: {
      ...save.arguments.target, changes: save.arguments.changes },
    editor_retained: { draft_ref: await ref.innerText(
      ), changes: { body: await body.inputValue() } },
  });
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'false');
  await expect(article.getByRole('button', { name: 'Save now' })).toBeDisabled();
  await article.getByRole('button', { name:
    'Discard changes and reload' }).click();
  await expect(body).toHaveValue(initial + '\nChanged on server\n');
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'true');
  expect(calls('atom_lifecycle_update')).toHaveLength(1);
}

for (const scenario of cases.guard_draft_editor) {
  test(`formal Draft guard: ${scenario.name}`, async ({ page }) => {
    const draft = await dirtyDraft(page, scenario.name === 'save_refused');
    if (scenario.name === 'rename_inactive') await renameInactive(
      scenario, draft);
    else if (scenario.name === 'discarded') await discardEdits(scenario, draft);
    else if (scenario.name === 'saved') await saveEdits(scenario, draft);
    else if (scenario.name === 'save_refused') await refuseEdits(
      scenario, draft);
    else throw new Error(`Unknown Draft guard case: ${scenario.name}`);
  });
}

for (const scenario of cases.observe_atom_lifecycle) {
  if (scenario.input.operation === 'current_draft') {
    for (const highest of [1, 4]) {
      test(`formal lifecycle: ${scenario.name} after version ${highest}`,
        ({ page }) => currentDraft(page, scenario, highest));
    }
    continue;
  }
  test(`formal lifecycle: ${scenario.name}`, async ({ page }) => {
    const [target, outcome, expected] = scenario.effect;
    expect([target, outcome]).toEqual(['C46.lifecycle_observation', 'observed']);
    if (scenario.input.operation === 'task_edit') await taskEdit(
      page, scenario.input, expected);
    else if (scenario.input.operation === 'configured_status') await configuredStatus(
      page, scenario.input, expected);
    else if (scenario.input.operation === 'principle_create') await principleCreate(
      page, scenario.input, expected);
    else if (scenario.input.operation === 'spec_activate') await specActivate(
      page, scenario.input, expected);
    else throw new Error(`Unknown lifecycle case: ${scenario.input.operation}`);
  });
}
