import { formalCases } from './console-formal-cases';
import { expect, test, type Page } from '@playwright/test';
import { mockGraph } from './console-graph-mock';
import { isToolCall } from './tool_rest_fixture';

type Detail = { view: string; depth?: number; types?
  : string; layout?: string; structure?: boolean;
  nodes?: string; edges?: string; red?:
    boolean; error?: string; seed?: string };
type Case = { name: string; input: Detail; effect: [string, string, Detail] };
const cases = formalCases<Case>('observe_console_graph').observe_console_graph;
test.use({ actionTimeout: 5000 });

async function setGraphInputs(page: Page, detail: Detail) {
  const graph = page.getByRole('region', { name: 'Atom Graph' });
  if (detail.depth !== undefined && detail.depth < 0) {
    await graph.getByLabel('Depth').fill(String(detail.depth));
    await graph.getByRole('button', { name: 'Show related' }).click();
    return;
  }
  await graph.getByText('Relation types').click();
  for (const type of ['cycle', 'other', 'uses']) {
    const checkbox = graph.getByLabel(type, { exact: true });
    if ((detail.types ?? '').split('|').includes(type)) await checkbox.check();
    else await checkbox.uncheck();
  }
  if (detail.structure) await graph.getByLabel(
    'Components and Packages with Spec Bindings').check();
  await graph.getByLabel('Depth').fill(String(detail.depth));
  await graph.getByRole('button', { name: 'Show related' }).click();
  if (detail.layout === 'horizontal') {
    const first = graph.locator('.node').filter({ hasText: 'AN-S-1' });
    const second = graph.locator('.node').filter({ hasText: 'AN-S-2' });
    await expect(second).toBeVisible();
    const a = await first.boundingBox(), b = await second.boundingBox();
    expect(b!.x).toBeGreaterThan(a!.x);
  }
}

async function checkVisible(page: Page, detail: Detail) {
  if (detail.error) { await expect(page.getByRole(
    'alert')).toContainText(detail.error); return; }
  const graph = page.getByRole('region', { name:
    detail.view === 'graph' ? 'Atom Graph' : 'Imports Graph' });
  const nodes = detail.nodes ? detail.nodes.split('|') : [];
  await expect(graph.locator('.node')).toHaveCount(nodes.length);
  if (detail.layout) await expect(
    graph).toHaveAttribute('data-layout', detail.layout);
  for (const node of nodes) await expect(graph.locator(
    '.node').filter({ hasText: node })).toBeVisible();
  const edges = detail.edges ? detail.edges.split('|') : [];
  if (edges.length) {
    await graph.getByText('Graph edges').click();
    await expect(graph.locator('details ul li')).toHaveCount(edges.length);
    await expect.poll(async () => (await graph.locator(
      'details ul li').allTextContents())
      .map(text => text.replace(/\s+/g, ' ').trim().replace(
        ' · ', ': ')).sort()).toEqual([...edges].sort());
  } else await expect(graph.locator('svg line, svg > path')).toHaveCount(0);
  if (detail.red) await expect(graph.locator(
    'line.violation')).toHaveCSS('stroke', 'rgb(204, 34, 34)');
}

for (const scenario of cases) {
  test(`formal graph: ${scenario.name}`, async ({ page }) => {
    const [target, outcome, expected] = scenario.effect;
    const detail = scenario.input;
    expect([target, outcome]).toEqual(['C46.graph_observation', 'visible']);
    await mockGraph(page, detail.view, detail.layout, undefined, detail.seed);
    await page.goto(`${process.env.WORKBENCH_E2E_URL}?workspace=formal-graph`);
    if (detail.view === 'graph') await setGraphInputs(page, detail);
    await checkVisible(page, { ...expected, view: detail.view });
    if (detail.seed) {
      const request = page.waitForRequest(request => isToolCall(request) &&
        request.postDataJSON()?.name === 'iwe_console_atom_document');
      const graph = page.getByRole('region', { name: 'Atom Graph' });
      await graph.locator('.node').getByRole('button',
        { name: detail.seed, exact: true }).click();
      expect((await request).postDataJSON(
        ).arguments.ref_id).toBe(detail.seed);
      await expect(page.getByRole('dialog', { name:
        'Atom document' })).toContainText(detail.seed);
    }
  });
}
