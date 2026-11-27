import { expect, test } from '@playwright/test';
import { mockDocuments } from './console-documents-fixture';

test('opens Atom links in modal, pane, and tab with exact history',
  async ({ page }) => {
  const requests = await mockDocuments(page);
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=fixture`);
  const gridLink = page.getByRole('grid').getByRole(
    'button', { name: 'AN-S-1', exact: true });
  await gridLink.click();
  const modal = page.getByRole('dialog', { name: 'Atom document' });
  await expect(modal).toContainText('AN-S-1@2');
  await modal.getByRole('button', { name: 'AN-S-1@1.md' }).click();
  await expect(modal).toContainText('AN-S-1@1');
  expect(requests).toContain('AN-S-1@1');
  await modal.getByRole('button', { name: 'Close', exact: true }).click();
  await gridLink.click({ button: 'right' });
  await page.getByText('Open in pane', { exact: true }).click();
  const pane = page.getByRole('complementary', { name: 'Atom document pane' });
  await expect(pane).toContainText('Body AN-S-2');
  const bodyLink = pane.getByRole('button',
    { name: 'AN-S-2', exact: true }).first();
  for (const key of ['ContextMenu', 'Shift+F10']) {
    await bodyLink.focus();
    await bodyLink.press(key);
    await expect(pane.getByRole('menuitem', {
      name: 'Open in modal' })).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(bodyLink).toBeFocused();
    await expect(pane.getByRole('menu')).toHaveCount(0);
  }
  await pane.getByRole('button', { name: 'Hide all' }).click();
  await expect(pane.getByRole('button', { name:
    'AN-S-1.md', exact: true })).toBeVisible();
  await expect(pane.getByText('Body AN-S-2')).toBeHidden();
  await pane.getByRole('button', { name: 'Expand all' }).click();
  await expect(pane).toContainText('Body AN-S-2');
  await pane.getByRole('button', { name: 'Close pane' }).click();
  await gridLink.click({ button: 'right' });
  await page.getByText('Open in new tab', { exact: true }).click();
  await expect(page.getByRole('tab', { name:
    /^AN-S-1(?: \*)?$/ })).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('.console-results')).toContainText('Body AN-S-2');
});

test('opens the full Atom reference when the grid truncates its label',
  async ({ page }) => {
  const requests = await mockDocuments(page, false, ['AN-S-1234']);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByLabel('Inline content character limit').fill('7');
  await page.getByRole('grid').getByRole('button',
    { name: 'AN-S-12', exact: true }).click();
  await expect(page.getByRole('dialog', {
    name: 'Atom document' })).toBeVisible();
  await expect.poll(() => requests.at(-1)).toBe('AN-S-1234');
});

test('keeps repeated Atom rows in Document query results',
  async ({ page }) => {
  await mockDocuments(page, false, ['AN-S-1', 'AN-S-1@1', 'AN-S-1']);
  await page.goto(process.env.WORKBENCH_E2E_URL!);
  await page.getByRole('combobox', { name: 'View',
    exact: true }).selectOption('document');
  await page.getByRole('button', { name: /^Run Cmd/ }).click();
  const headings = page.locator('.document-stack button.heading');
  await expect(headings).toHaveText(['AN-S-1.md', 'AN-S-1@1.md', 'AN-S-1.md']);
});

test('opens exact Atom documents from a full cell value and grouped results',
  async ({ page }) => {
  const ref = 'AN-S-1@1';
  const requests = await mockDocuments(page,
    false, [`${ref}-SPEC--example.md`]);
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=grid-links`);
  const cell = page.locator('.tabulator-cell').first();
  const modal = page.getByRole('dialog', { name: 'Atom document' });
  await cell.click({ button: 'right' });
  await page.getByText('Cell Show full value', { exact: true }).click();
  await page.getByRole('dialog', { name: 'Full cell value' })
    .getByRole('button', { name: ref, exact: true }).click();
  await expect(modal).toContainText(ref);
  expect(requests.at(-1)).toBe(ref);
  await modal.getByRole('button', { name: 'Close', exact: true }).click();
  await page.getByRole('columnheader').first().click({ button: 'right' });
  await page.getByText('Group by', { exact: true }).click();
  await page.locator('.tabulator-group').getByRole(
    'button', { name: ref, exact: true }).click();
  await expect(modal).toContainText(ref);
  expect(requests).toEqual([ref, ref]);
});
