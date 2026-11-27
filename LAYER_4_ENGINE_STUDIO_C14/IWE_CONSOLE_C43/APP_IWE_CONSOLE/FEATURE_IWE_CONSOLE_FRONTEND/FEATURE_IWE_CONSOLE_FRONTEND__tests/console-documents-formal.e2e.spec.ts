import { formalCases } from './console-formal-cases';
import { expect, test, type Page } from '@playwright/test';
import { mockDocuments } from './console-documents-fixture';

type Detail = { source: string; reference?: string; destination?: string; exact_ref?: string;
  operation?: string; visible?: string; history?: boolean; related?: boolean; contained?: boolean };
type Case = { name: string; input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>('observe_atom_document').observe_atom_document;

async function tableNavigation(page: Page, detail: Detail, expected: Detail) {
  await mockDocuments(page);
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=formal-document`);
  const link = page.getByRole('grid').getByRole('button', { name: detail.reference, exact: true });
  if (detail.destination === 'modal') await link.click();
  else {
    await link.click({ button: 'right' });
    await page.getByText(detail.destination === 'pane' ? 'Open in pane' : 'Open in new tab', { exact: true }).click();
  }
  const area = detail.destination === 'modal' ? page.getByRole('dialog', { name: 'Atom document' }) :
    detail.destination === 'pane' ? page.getByRole('complementary', { name: 'Atom document pane' }) : page.locator('.console-results');
  await expect(area).toContainText(expected.exact_ref!);
  if (detail.destination === 'tab') await expect(page.getByRole('tab', { name: /^AN-S-1(?: \*)?$/ })).toHaveAttribute('aria-selected', 'true');
}

async function graphNavigation(page: Page, detail: Detail) {
  await mockDocuments(page, true);
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=formal-graph-document`);
  const link = page.getByRole('region', { name: 'Atom Graph' }).getByRole('button', { name: detail.reference, exact: true });
  if (detail.destination === 'modal') await link.click();
  else {
    await link.click({ button: 'right' });
    await page.getByRole('menuitem', { name: detail.destination === 'pane' ? 'Open in pane' : 'Open in tab' }).click();
  }
  const area = detail.destination === 'modal' ? page.getByRole('dialog', { name: 'Atom document' }) :
    detail.destination === 'pane' ? page.getByRole('complementary', { name: 'Atom document pane' }) : page.locator('.console-results');
  await expect(area).toContainText('AN-S-1@2');
  if (detail.destination === 'tab') await expect(page.getByRole('tab', { name: /^AN-S-1(?: \*)?$/ })).toHaveAttribute('aria-selected', 'true');
}

async function documentObservation(page: Page, detail: Detail) {
  const requests = await mockDocuments(page);
  await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=formal-document`);
  await page.getByRole('grid').getByRole('button', { name: 'AN-S-1', exact: true }).click();
  const modal = page.getByRole('dialog', { name: 'Atom document' });
  if (detail.operation === 'open_related' || detail.operation === 'open_contained') {
    const label = detail.operation === 'open_related' ? 'AN-S-2' : 'AN-T-5.md';
    await modal.getByRole('button', { name: label, exact: true }).last().click();
    await expect.poll(() => requests.at(-1)).toBe(detail.reference);
    return;
  }
  if (detail.history) {
    for (const status of ['Archived', 'Ready', 'Draft']) await expect(modal.getByRole('listitem').filter({ hasText: status })).toBeVisible();
    if (detail.related) await expect(modal.getByRole('heading', { name: 'Relations' })).toBeVisible();
    if (detail.contained) await expect(modal.getByRole('button', { name: 'AN-T-5.md' })).toBeVisible();
    await modal.getByRole('button', { name: 'AN-S-1@1.md' }).click();
    const exactLink = modal.getByRole('button', { name: 'AN-S-1@1', exact: true });
    await exactLink.click({ button: 'right' });
    await modal.getByRole('menuitem', { name: 'Open in pane' }).click();
    const pane = page.getByRole('complementary', { name: 'Atom document pane' });
    await expect(pane.getByRole('button', { name: 'AN-S-1@1', exact: true })).toBeVisible();
    return;
  }
  await modal.getByRole('button', { name: 'Open in pane', exact: true }).click();
  const pane = page.getByRole('complementary', { name: 'Atom document pane' });
  if (detail.related) await expect(pane.getByRole('heading', { name: 'Relations' })).toBeVisible();
  if (detail.contained) await expect(pane.getByRole('button', { name: 'AN-T-5.md' })).toBeVisible();
  await pane.getByRole('button', { name: 'Hide all' }).click();
  await expect(pane.getByRole('button', { name: 'AN-S-1.md', exact: true })).toBeVisible();
  await expect(pane.getByText('Body AN-S-2')).toBeHidden();
  if (detail.operation === 'expand_all') {
    await pane.getByRole('button', { name: 'Expand all' }).click();
    await expect(pane).toContainText('Body AN-S-2');
  }
}

for (const scenario of cases) {
  test(`formal document: ${scenario.name}`, async ({ page }) => {
    const [target, outcome, expected] = scenario.effect;
    const detail = scenario.input;
    expect([target, outcome]).toEqual(['C46.document_observation', 'observed']);
    if (detail.source === 'table') await tableNavigation(page, detail, expected);
    else if (detail.source === 'graph') await graphNavigation(page, detail);
    else await documentObservation(page, { ...expected, ...detail });
  });
}
