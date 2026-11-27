import type { Page } from '@playwright/test';
import { graphQueryResponse } from './console-graph-mock';

export async function mockDocuments(page: Page, graph = false, refs = ['AN-S-1', 'AN-S-1@1']) {
  const requests: string[] = [];
  const run = { status: 'success', query_id: 'q1', revision: 1 };
  const views = [{ id: 'v1', name: 'Source', sql: `SELECT reference FROM atoms${graph ? ' VIEW GRAPH' : ''}`, cursor_position: 0, revision: 1, result: run }];
  let active = 'v1';
  const state = () => ({ project_name: 'Fixture', workspace_id: 'test', active_view_id: active, views });
  const result = () => ({ query_id: 'q1', columns: [{ name: 'ref', type: 'VARCHAR', has_values: true }], rows: refs.map((ref) => [ref]), row_count: refs.length, offset: 0, page_size: 100, has_more: false });
  await page.route('**/*', async (route) => {
    if (route.request().method() !== 'POST') return route.continue();
    const path = new URL(route.request().url()).pathname;
    if (!path.endsWith('/interface')) {
      if (path.endsWith('/run')) return route.fulfill({ json: graphQueryResponse(route.request().postDataJSON().sql) });
      const value = path.endsWith('/schema') ? { tables: [] } : path.endsWith('/status') ? { mode: 'unavailable' } : { items: [] };
      return route.fulfill({ json: value });
    }
    const { operation, arguments: args } = route.request().postDataJSON();
    let value: unknown = {};
    if (operation === 'workspace_get' || operation === 'workspace_open') value = state();
    if (operation === 'view_fetch') value = {
      ...result(), ...(args.grid?.group_by && { groups: refs.map((ref) => ({ value: ref, count: 1 })) }),
    };
    if (operation === 'query_log_list') value = { items: [] };
    if (operation === 'view_focus') { active = args.view_id; value = state(); }
    if (operation === 'view_create') {
      active = `v${views.length + 1}`;
      views.push({ id: active, name: args.name, sql: '', cursor_position: 0, revision: 1, result: run });
      value = { ...state(), view_id: active };
    }
    if (operation === 'view_update') {
      const view = views.find((item) => item.id === args.view_id)!;
      view.sql = args.sql; view.revision++; value = view;
    }
    if (operation === 'view_run') value = { ...run, revision: views.find((item) => item.id === args.view_id)!.revision };
    if (operation === 'iwe_console_atom_document') {
      const ref = args.ref_id as string; requests.push(ref);
      value = documentResponse(ref);
    }
    await route.fulfill({ json: value });
  });
  return requests;
}

function documentResponse(ref: string) {
  return { ref_id: 'AN-S-1', exact_ref: ref.includes('@') ? ref : 'AN-S-1@2', version: ref.includes('@') ? 1 : 2,
        status: 'Current', filename: ref.includes('@') ? 'AN-S-1@1.md' : 'AN-S-1.md', body: 'Body AN-S-2',
        history: ref.includes('@') ? [] : [
          { ref_id: 'AN-S-1@1', version: 1, status: 'Archived', filename: 'AN-S-1@1.md' },
          { ref_id: 'AN-S-1@3-ready', version: 3, status: 'Ready', filename: 'AN-S-1@3-ready.md' },
          { ref_id: 'AN-S-1@4-draft', version: 4, status: 'Draft', filename: 'AN-S-1@4-draft.md' },
        ], relations: [{ type: 'USES', ref_id: 'AN-S-2', direction: 'outgoing', derived: false }],
        contained: [{ ref_id: 'AN-T-5', filename: 'AN-T-5.md' }] };
}
