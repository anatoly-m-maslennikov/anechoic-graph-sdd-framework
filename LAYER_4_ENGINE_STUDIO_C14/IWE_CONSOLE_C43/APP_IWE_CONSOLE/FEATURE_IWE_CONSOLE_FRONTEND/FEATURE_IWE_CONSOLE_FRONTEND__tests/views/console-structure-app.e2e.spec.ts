import { expect, test } from '@playwright/test';
import { formalCases } from '../unit/support/support__shared';
import { mockGraph } from '../unit/support/support__shared';

test('Structure displays Component and Seed links in the App',
  async ({ page }) => {
  await mockGraph(page, 'structure');
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=structure-app`);
  const structure = page.getByRole('list', { name: 'Project Structure' });
  const component = structure.getByRole(
    'listitem').filter({ hasText: 'Component One' });
  const seed = structure.getByRole('listitem').filter({ hasText: 'Seed One' });
  await expect(component).toContainText('Purpose');
  await expect(seed).toContainText('Seed purpose');
  await expect(component.getByRole('button',
    { name: 'Manifest' })).toBeVisible();
  await expect(component.getByRole('button',
    { name: 'Solution' })).toBeVisible();
  await expect(seed.getByRole('button', { name: 'Manifest' })).toBeVisible();
  await expect(seed.getByRole('button', { name: 'Solution' })).toBeVisible();
  const dialog = page.getByRole('dialog', { name: 'Atom document' });
  await component.getByRole('button', {
    name: 'AN-S-1@2', exact: true }).click();
  await expect(dialog).toContainText('AN-S-1@2');
  await dialog.getByRole('button', { name: 'Close', exact: true }).click();
  await seed.getByRole('button', { name: 'Manifest' }).click();
  await expect(dialog).toContainText('AN-S-3@1');
});


type Detail = { row: string; action?: string;
  purpose?: string; reference?: string };
type Case = { name: string; input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>(
  'observe_console_structure').observe_console_structure;

for (const scenario of cases) {
  test(`formal structure: ${scenario.name}`, async ({ page }) => {
    const [target, outcome, expected] = scenario.effect;
    expect([target, outcome]).toEqual([
      'C46.structure_observation', 'observed']);
    await mockGraph(page, 'structure');
    await page.goto(
      `${process.env.WORKBENCH_E2E_URL}?workspace=formal-structure`);
    const row = page.getByRole('list', { name: 'Project Structure' })
      .getByRole('listitem').filter({ hasText: scenario.input.row });
    if (expected.purpose) await expect(row.locator(
      'p')).toHaveText(expected.purpose);
    if (scenario.input.action) {
      await row.getByRole('button', { name: scenario.input.action }).click();
      await expect(page.getByRole('dialog', { name: 'Atom document' })
        .getByRole('button', { name: expected.reference,
          exact: true })).toBeVisible();
    }
  });
}
