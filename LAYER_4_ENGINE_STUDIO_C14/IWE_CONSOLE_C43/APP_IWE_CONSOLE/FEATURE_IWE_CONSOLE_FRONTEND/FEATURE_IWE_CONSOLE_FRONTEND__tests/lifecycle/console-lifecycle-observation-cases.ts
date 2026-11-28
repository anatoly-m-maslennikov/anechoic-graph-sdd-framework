import { expect, type Page } from '@playwright/test';
import { lifecycleFixture } from './console-lifecycle-fixture';

export type Detail = { operation?: string; family?: string;
  template?: string; tier?: number; lens?: string;
  target_status?: string; autosave_seconds?: number; removed_type?
    : string; removed_ref?: string; authored_only?: boolean;
  publish_status?: string; current_status?: string;
    reopens_existing?: boolean; component?: string; error?: string;
  current_body?: string; ticket_statuses?: string[]; pending_save?: boolean };

export async function taskEdit(page: Page, input: Detail, expected: Detail) {
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

export async function principleCreate(page: Page, input: Detail, expected: Detail) {
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

export async function specActivate(page: Page, input: Detail, expected: Detail) {
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

