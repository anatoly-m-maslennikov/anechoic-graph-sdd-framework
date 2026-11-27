import { expect, test, type Page } from '@playwright/test';
import { checkObservedValues, formalCases, type CorrelatedCase } from './console-formal-cases';

type Detail = { operation?: string; family?: string; template?: string; tier?: number; lens?: string;
  target_status?: string; autosave_seconds?: number; removed_type?: string; removed_ref?: string; authored_only?: boolean;
  publish_status?: string; current_status?: string; reopens_existing?: boolean; component?: string; error?: string;
  current_body?: string; ticket_statuses?: string[] };
type Case = CorrelatedCase & { input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>('observe_atom_lifecycle', 'guard_draft_editor');
const authoredRelation = { type: 'IS_SOLUTION_FOR', ref_id: 'AN-S-1' };
const readOnlyRelations = [
  { type: 'CONTAINED_BY', ref_id: 'C00', direction: 'outgoing', derived: false },
  { type: 'DERIVED', ref_id: 'AN-S-2', direction: 'outgoing', derived: true },
  { type: 'INCOMING', ref_id: 'AN-S-3', direction: 'incoming', derived: false },
];

function lifecycleTable(ref: string, inline?: boolean) {
  const run = { query_id: 'current', revision: 1, status: 'success' };
  const active = { id: 'view', name: 'Active View', sql: 'SELECT reference FROM atoms' + (inline ? ' VIEW DOCUMENT' : ''),
    revision: 1, cursor_position: 0, result: run };
  const other = { id: 'other', name: 'Other View', sql: 'SELECT 2', revision: 1, cursor_position: 0 };
  const workspace = { workspace_id: 'test', project_name: 'Test', active_view_id: active.id, views: inline ? [active, other] : [active] };
  const result = { query_id: run.query_id, columns: [{ name: 'reference', type: 'VARCHAR' }],
    rows: [[ref]], row_count: 1, offset: 0, page_size: 100, has_more: false };
  return { workspace, result, other };
}

function lifecycleDocuments(family: string, hasDraft: boolean, highest: number, ticketStatuses?: string[]) {
  const stable = `AN-${family}-1`;
  const draftVersion = hasDraft ? 1 : highest + 1;
  const exact = `${stable}@${draftVersion}-draft`;
  const publishStatus = family === 'S' ? 'ready' : 'backlog';
  let body = '## Summary\n\nCreated\n'; let stamp = 'one'; let removed = false; let currentStatus = publishStatus;
  const history = [
    { ref_id: stable, version: 1, status: publishStatus, filename: 'current.md' },
    ...(highest > 1 ? [{ ref_id: `${stable}@${highest}`, version: highest, status: 'archived', filename: 'archived.md' }] : []),
    { ref_id: exact, version: draftVersion, status: 'draft', filename: 'draft.md' },
  ].filter((revision) => hasDraft || revision.status !== 'draft');
  const document = (ref: string) => ({ ref_id: stable, exact_ref: ref === exact ? exact : stable,
    version: ref === exact ? draftVersion : 1, status: ref === exact ? 'draft' : currentStatus, filename: ref === exact ? 'draft.md' : 'current.md',
    ...(ticketStatuses && ref !== exact ? { ticket_statuses: ticketStatuses } : {}),
    authored_relations: ref === exact && !removed ? [authoredRelation] : [],
    body, updated_at: stamp, template: family === 'S' ? 'axiom' : 'task', history, contained: [],
    relations: removed ? readOnlyRelations : [
      { ...authoredRelation, direction: 'outgoing', derived: false }, ...readOnlyRelations,
    ] });
  function save(changes: { body?: string; removeRelations?: unknown[] }, refuse?: boolean) {
    if (refuse) {
      body = '## Summary\n\nCreated\n\nChanged on server\n'; stamp = 'newer';
      return { status: 'failed', errors: [{ code: 'source_changed', message: 'Draft updated_at does not match the expected timestamp.' }] };
    }
    if (changes.body) body = changes.body;
    if (changes.removeRelations) removed = true;
    stamp = 'two'; return { status: 'completed', artifact: { ref_id: exact, updated_at: stamp } };
  }
  return { stable, exact, draftVersion, publishStatus, document, save,
    changeStatus(status: string) { currentStatus = status; } };
}

async function lifecycleFixture(page: Page, family = 'T', hasDraft = true, ticketStatuses?: string[],
  options: { inline?: boolean; refuseSave?: boolean; refuseCreate?: boolean; highestVersion?: number } = {}) {
  const calls: { operation: string; arguments: any; reply: any }[] = [];
  const docs = lifecycleDocuments(family, hasDraft, options.highestVersion ?? 1, ticketStatuses);
  const { stable, exact, draftVersion, publishStatus } = docs;
  const table = lifecycleTable(options.inline ? exact : stable, options.inline);
  await page.route('**/*', async (route) => {
    const request = route.request();
    if (request.method() !== 'POST') return route.continue();
    const path = new URL(request.url()).pathname;
    if (!path.endsWith('/interface')) {
      return route.fulfill({ json: path.endsWith('/schema') ? { tables: {} } : path.endsWith('/status') ? { mode: 'unavailable' } : { items: [] } });
    }
    const input = request.postDataJSON();
    const args = input.arguments;
    let result: unknown = {};
    switch (input.operation) {
      case 'workspace_open': case 'workspace_get': result = table.workspace; break;
      case 'view_rename': table.other.name = args.name; result = { ...table.other }; break;
      case 'view_fetch': result = table.result; break;
      case 'iwe_console_atom_document': result = docs.document(args.ref_id); break;
      case 'atom_lifecycle_create_draft': result = options.refuseCreate ? { status: 'failed', errors: [{ message: 'fixture stop' }] }
        : { status: 'completed', savedDraft: { ref_id: exact, version: draftVersion } }; break;
      case 'atom_lifecycle_update': result = docs.save(args.changes, options.refuseSave); break;
      case 'atom_lifecycle_promote_draft': expect(args.targetStatus).toBe(publishStatus); result = { status: 'completed', artifact: { ref_id: stable } }; break;
      case 'atom_lifecycle_change_status': expect(args.targetStatus).toBe(ticketStatuses ? ticketStatuses[1] : family === 'S' ? 'active' : 'in_queue'); docs.changeStatus(args.targetStatus); result = { status: 'completed', artifact: { ref_id: stable } }; break;
      case 'query_log_list': result = { items: [] }; break;
    }
    calls.push({ ...input, reply: result });
    return route.fulfill({ json: result });
  });
  return { calls, stable, exact };
}

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
  await expect.poll(() => calls.filter((c) => c.operation === 'atom_lifecycle_update').length, { timeout: 8000 }).toBe(1);
  const update = calls.find((c) => c.operation === 'atom_lifecycle_update')!.arguments;
  expect(update).toEqual({ target: { ref_id: exact, version: 1 }, expectedUpdatedAt: 'one',
    changes: { body: '## Summary\n\nCreated\n\nEdited\n', removeRelations: [{ type: expected.removed_type, ref_id: expected.removed_ref }] } });
  await expect(dialog.getByText('Saved', { exact: true })).toBeVisible();
  await editor.fill('## Summary\n\nCreated\n\nFinal edit\n');
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  await expect.poll(() => calls.some(call => call.operation === 'atom_lifecycle_promote_draft')).toBe(true);
  expect(calls.find((c) => c.operation === 'atom_lifecycle_promote_draft')?.arguments.targetStatus).toBe(expected.publish_status);
  const mutations = calls.filter((c) => ['atom_lifecycle_update', 'atom_lifecycle_promote_draft'].includes(c.operation));
  expect(mutations.map((c) => c.operation)).toEqual(['atom_lifecycle_update', 'atom_lifecycle_update', 'atom_lifecycle_promote_draft']);
  expect(mutations[1].arguments).toMatchObject({ expectedUpdatedAt: 'two', changes: { body: '## Summary\n\nCreated\n\nFinal edit\n' } });
  await expect(dialog.getByRole('button', { name: 'Edit Draft' })).toBeVisible();
  await dialog.getByRole('button', { name: 'Change status' }).click();
  await expect.poll(() => calls.some((c) => c.operation === 'atom_lifecycle_change_status')).toBe(true);
  expect(calls.find((c) => c.operation === 'atom_lifecycle_change_status')?.arguments.targetStatus).toBe(expected.current_status);
  await dialog.getByRole('button', { name: 'Edit Draft' }).click();
  await expect(dialog.getByRole('button', { name: 'Promote Draft' })).toBeVisible();
  expect(calls.filter((c) => c.operation === 'atom_lifecycle_create_draft')).toHaveLength(expected.reopens_existing ? 1 : 2);
}

async function principleCreate(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page, 'S', false, undefined, { refuseCreate: true });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByText('Create Atom', { exact: true }).click();
  await page.locator('form').getByLabel('Template').selectOption(input.template!);
  await page.locator('form').getByLabel('Tier').selectOption(String(input.tier));
  await page.locator('form').getByLabel('Lens').fill(input.lens!);
  await page.getByLabel('Body', { exact: true }).fill('## Summary\n\nPrinciple\n');
  await page.getByRole('button', { name: 'Create Draft' }).click();
  await expect(page.getByRole('alert')).toContainText(expected.error!);
  expect(calls.find(call => call.operation === 'atom_lifecycle_create_draft')?.arguments).toEqual({
    newAtom: { template: expected.template, container: { component: expected.component }, lens: expected.lens, tier: expected.tier, body: '## Summary\n\nPrinciple\n' } });
}

async function specActivate(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page, input.family);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByText('Create Atom', { exact: true }).click();
  await page.locator('form').getByLabel('Template').selectOption(input.template!);
  await page.getByLabel('Body', { exact: true }).first().fill('## Summary\n\nCreated\n');
  await page.getByRole('button', { name: 'Create Draft' }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await dialog.getByLabel('Body', { exact: true }).fill(expected.current_body!);
  await dialog.getByRole('combobox', { name: 'Status' }).selectOption(input.target_status!);
  await dialog.getByRole('button', { name: 'Promote Draft' }).click();
  await expect(dialog.getByText('AN-S-1 · active')).toBeVisible();
  await expect(dialog.locator('.atom-document .body')).toHaveText(expected.current_body!);
  const writes = calls.filter((entry) => entry.operation.includes('promote_draft') || entry.operation.includes('change_status'));
  expect(writes.map((entry) => [entry.operation, entry.arguments.targetStatus])).toEqual([
    ['atom_lifecycle_promote_draft', expected.publish_status],
    ['atom_lifecycle_change_status', expected.current_status],
  ]);
}

async function currentDraft(page: Page, scenario: Case, highestVersion: number) {
  const { calls, stable } = await lifecycleFixture(page, scenario.input.family, false, undefined, { highestVersion });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('grid').getByRole('button', { name: stable, exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await dialog.getByRole('button', { name: 'Edit Draft' }).click();
  await expect(dialog.getByRole('button', { name: 'Promote Draft' })).toBeVisible();
  const relevant = calls.filter(call => ['iwe_console_atom_document', 'atom_lifecycle_create_draft'].includes(call.operation));
  expect(relevant.map(call => call.operation)).toEqual(['iwe_console_atom_document', 'atom_lifecycle_create_draft', 'iwe_console_atom_document']);
  const [source, create, opened] = relevant;
  const returned = create.reply.savedDraft;
  expect(returned.ref_id).toBe(`${stable}@${highestVersion + 1}-draft`);
  const sourceFields = { source_ref: source.reply.ref_id, source_version: source.reply.version };
  const displayed = await dialog.locator('.atom-document header > span .link').first().innerText();
  checkObservedValues(scenario, {
    current_draft: sourceFields, create_requested: create.arguments.sourceCurrent,
    draft_returned: returned, document_requested: opened.arguments,
    observed: { source_ref: create.arguments.sourceCurrent.ref_id, source_version: create.arguments.sourceCurrent.version, draft_ref: displayed },
  });
}

async function configuredStatus(page: Page, input: Detail, expected: Detail) {
  const { calls } = await lifecycleFixture(page, input.family, false, input.ticket_statuses);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('grid').getByRole('button', { name: 'AN-T-1', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  const statuses = dialog.getByRole('combobox', { name: 'Status' });
  await expect(statuses.locator('option')).toHaveText(['In queue', 'Waiting review']);
  await statuses.selectOption(expected.current_status!);
  await dialog.getByRole('button', { name: 'Change status' }).click();
  await expect.poll(() => calls.find((call) => call.operation === 'atom_lifecycle_change_status')?.arguments.targetStatus)
    .toBe(expected.current_status);
}

async function dirtyDraft(page: Page, refuseSave: boolean) {
  const fixture = await lifecycleFixture(page, 'T', true, undefined, { inline: true, refuseSave });
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  const article = page.locator('.document-stack .atom-document');
  const ref = article.locator('header > span .link').first();
  const body = article.getByLabel('Body', { exact: true });
  const other = page.getByRole('tab', { name: 'Other View', exact: true });
  const calls = (operation: string) => fixture.calls.filter(call => call.operation === operation);
  const initial = '## Summary\n\nCreated\n';
  await body.fill(initial + '\nLocal changes\n');
  const source = calls('workspace_open')[0].reply;
  const dirty = { draft_ref: await ref.innerText(), changes: { body: await body.inputValue() } };
  const activeId = async () => {
    const title = await page.getByRole('tab', { selected: true }).innerText();
    return source.views.find((view: { name: string }) => view.name === title)?.id;
  };
  return { page, article, ref, body, other, initial, dirty, source, activeId, calls, fixture };
}
type DirtyDraft = Awaited<ReturnType<typeof dirtyDraft>>;

async function renameInactive(scenario: Case, { page, article, body, other, dirty, source, activeId, calls }: DirtyDraft) {
  const original = { view_id: source.views.find((view: { name: string }) => view.name === 'Other View').id,
    name: 'Renamed View', active_view_id: await activeId() };
  await other.click({ button: 'right' });
  await page.getByRole('menuitem', { name: 'Rename', exact: true }).click();
  const field = page.getByRole('dialog', { name: 'View name' }).getByRole('textbox');
  await field.fill(original.name); await field.press('Enter');
  await expect(page.getByRole('tab', { name: original.name, exact: true })).toBeVisible();
  const [rename] = calls('view_rename');
  checkObservedValues(scenario, {
    rename_inactive: original, rename_requested: rename.arguments, rename_returned: rename.reply,
    view_observed: { active_view_id: await activeId() },
  });
  expect(calls('view_focus').some(call => call.arguments.view_id === original.view_id)).toBe(false);
  await expect(body).toHaveValue(dirty.changes.body);
  await article.getByRole('button', { name: 'Save now' }).click();
  await expect(article.getByText('Saved', { exact: true })).toBeVisible();
  expect(calls('atom_lifecycle_update')[0].arguments).toMatchObject({ target: { ref_id: dirty.draft_ref }, changes: dirty.changes });
}

async function discardEdits(scenario: Case, { article, ref, body, other, initial, dirty, calls }: DirtyDraft) {
  const confirmed = { draft_ref: await ref.innerText(), changes: { body: await body.inputValue() } };
  await article.getByRole('button', { name: 'Discard changes and reload' }).click();
  await expect(body).toHaveValue(initial);
  const reloaded = calls('iwe_console_atom_document').at(-1)!.arguments.ref_id;
  await other.click();
  await expect(body).toHaveCount(0);
  expect(calls('atom_lifecycle_update')).toHaveLength(0);
  checkObservedValues(scenario, { leave_dirty: dirty, discard_confirmed: confirmed, editor_unmounted: { draft_ref: reloaded } });
}

async function saveEdits(scenario: Case, { ref, body, other, dirty, calls, fixture }: DirtyDraft) {
  const departing = await ref.innerText();
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'true');
  await expect(body).toHaveCount(0);
  const [save] = calls('atom_lifecycle_update');
  const relevant = fixture.calls.filter(call => ['atom_lifecycle_update', 'view_focus'].includes(call.operation));
  expect(relevant.map(call => call.operation)).toEqual(['atom_lifecycle_update', 'view_focus']);
  checkObservedValues(scenario, {
    leave_dirty: dirty, save_requested: { ...save.arguments.target, changes: save.arguments.changes },
    save_succeeded: save.reply.artifact, editor_unmounted: { draft_ref: departing },
  });
}

async function refuseEdits(scenario: Case, { article, ref, body, other, initial, dirty, calls }: DirtyDraft) {
  await other.click();
  await expect(article.getByRole('alert')).toHaveText('Draft updated_at does not match the expected timestamp.');
  const [save] = calls('atom_lifecycle_update');
  checkObservedValues(scenario, {
    leave_dirty: dirty, save_requested: { ...save.arguments.target, changes: save.arguments.changes },
    editor_retained: { draft_ref: await ref.innerText(), changes: { body: await body.inputValue() } },
  });
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'false');
  await expect(article.getByRole('button', { name: 'Save now' })).toBeDisabled();
  await article.getByRole('button', { name: 'Discard changes and reload' }).click();
  await expect(body).toHaveValue(initial + '\nChanged on server\n');
  await other.click();
  await expect(other).toHaveAttribute('aria-selected', 'true');
  expect(calls('atom_lifecycle_update')).toHaveLength(1);
}

for (const scenario of cases.guard_draft_editor) {
  test(`formal Draft guard: ${scenario.name}`, async ({ page }) => {
    const draft = await dirtyDraft(page, scenario.name === 'save_refused');
    if (scenario.name === 'rename_inactive') await renameInactive(scenario, draft);
    else if (scenario.name === 'discarded') await discardEdits(scenario, draft);
    else if (scenario.name === 'saved') await saveEdits(scenario, draft);
    else if (scenario.name === 'save_refused') await refuseEdits(scenario, draft);
    else throw new Error(`Unknown Draft guard case: ${scenario.name}`);
  });
}

for (const scenario of cases.observe_atom_lifecycle) {
  if (scenario.input.operation === 'current_draft') {
    for (const highest of [1, 4]) {
      test(`formal lifecycle: ${scenario.name} after version ${highest}`, ({ page }) => currentDraft(page, scenario, highest));
    }
    continue;
  }
  test(`formal lifecycle: ${scenario.name}`, async ({ page }) => {
    const [target, outcome, expected] = scenario.effect;
    expect([target, outcome]).toEqual(['C46.lifecycle_observation', 'observed']);
    if (scenario.input.operation === 'task_edit') await taskEdit(page, scenario.input, expected);
    else if (scenario.input.operation === 'configured_status') await configuredStatus(page, scenario.input, expected);
    else if (scenario.input.operation === 'principle_create') await principleCreate(page, scenario.input, expected);
    else if (scenario.input.operation === 'spec_activate') await specActivate(page, scenario.input, expected);
    else throw new Error(`Unknown lifecycle case: ${scenario.input.operation}`);
  });
}
