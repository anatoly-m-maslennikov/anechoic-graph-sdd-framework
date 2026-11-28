import { taskEdit, principleCreate, specActivate,
  type Detail } from './console-lifecycle-observation-cases';
import { expect, test, type Page } from '@playwright/test';
import { checkObservedEffects, checkObservedValues, formalCases,
  type CorrelatedCase } from '../unit/support/support__shared';
import { attachDraftGuardTrace, lifecycleFixture, observeLifecycle,
  watchAppearance, watchDraft } from './console-lifecycle-fixture';
import { isToolCall } from '../unit/support/support__shared';

type Case = CorrelatedCase & { input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>('observe_atom_lifecycle', 'guard_draft_editor');

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

async function dirtyDraft(page: Page,
  options: Parameters<typeof lifecycleFixture>[4], trackSavePhase = false) {
  const fixture = await lifecycleFixture(page, 'T',
    true, undefined, { ...options, inline: true });
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
  const effects = await observeLifecycle(page, trackSavePhase);
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

async function holdFirstSave(page: Page, draft: DirtyDraft,
  release: () => void, newer: string) {
  const { article, ref, body, other, dirty, calls } = draft;
  try {
    const requested = page.waitForRequest(request =>
      isToolCall(request) && request.postDataJSON().name === 'atom_lifecycle_update');
    await article.getByRole('button', { name: 'Save now' }).click();
    const earlier = await requested;
    expect(earlier.postDataJSON().arguments.changes).toEqual(dirty.changes);
    await body.fill(newer);
    const departure = { draft_ref: await ref.innerText(),
      changes: { body: await body.inputValue() } };
    await other.click();
    await expect(other).toHaveAttribute('aria-selected', 'false');
    expect(calls('view_focus')).toHaveLength(0);
    return departure;
  } finally {
    release();
  }
}

function pendingOutcome(scenario: Case) {
  const refuseSave = scenario.name === 'pending_save_refused';
  const refuseSecondSave = scenario.name === 'latest_save_refused';
  const saved = scenario.name === 'saved_after_pending';
  expect([refuseSave, refuseSecondSave, saved].filter(Boolean)).toHaveLength(1);
  return { refuseSave, refuseSecondSave, saved };
}

async function recordPendingTrace(scenario: Case, draft: DirtyDraft,
  departure: DirtyDraft['dirty'], saved: boolean) {
  const { calls, effects, ref, body } = draft;
  const observedEffects = await effects();
  checkObservedEffects(scenario, observedEffects);
  const [pending, latest] = calls('atom_lifecycle_update');
  const values = {
    leave_dirty: departure,
    pending_save_requested: { ...pending.arguments.target,
      changes: pending.arguments.changes },
    pending_save_succeeded: pending.reply.artifact ?? {},
    save_requested: latest ? { ...latest.arguments.target,
      changes: latest.arguments.changes,
      expectedUpdatedAt: latest.arguments.expectedUpdatedAt } : {},
    save_succeeded: latest?.reply.artifact ?? {},
    ...(saved ? { editor_unmounted: { draft_ref: departure.draft_ref } } :
      { editor_retained: { draft_ref: await ref.innerText(),
        changes: { body: await body.inputValue() } } }),
  };
  checkObservedValues(scenario, values);
  await attachDraftGuardTrace(scenario.name, observedEffects, values);
}

async function leaveDuringSave(page: Page, scenario: Case) {
  let release!: () => void;
  const waitForFirstSave = new Promise<void>(resolve => { release = resolve; });
  const { refuseSave, refuseSecondSave, saved } = pendingOutcome(scenario);
  const draft = await dirtyDraft(page,
    { waitForFirstSave, refuseSave, refuseSecondSave }, true);
  const { article, body, other, dirty, calls, fixture } = draft;
  const newer = dirty.changes.body + '\nEdited while saving\n';
  const departure = await holdFirstSave(page, draft, release, newer);
  if (saved) {
    await expect(other).toHaveAttribute('aria-selected', 'true');
    await expect(body).toHaveCount(0);
    await expect.poll(() => calls('view_focus').length).toBe(1);
  } else {
    await expect(article.getByRole('alert')).toHaveText(
      'Draft updated_at does not match the expected timestamp.');
    await expect(body).toHaveValue(newer);
    await expect(other).toHaveAttribute('aria-selected', 'false');
  }
  const writes = fixture.calls.filter(call => [
    'atom_lifecycle_update', 'view_focus'].includes(call.operation));
  expect(writes.map(call => call.operation)).toEqual([
    'atom_lifecycle_update',
    ...(refuseSave ? [] : ['atom_lifecycle_update']),
    ...(saved ? ['view_focus'] : []),
  ]);
  await recordPendingTrace(scenario, draft, departure, saved);
}
for (const scenario of cases.guard_draft_editor) {
  test(`formal Draft guard: ${scenario.name}`, async ({ page }) => {
    if (scenario.input.pending_save) return leaveDuringSave(page, scenario);
    const draft = await dirtyDraft(page, { refuseSave: scenario.name === 'save_refused' });
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
