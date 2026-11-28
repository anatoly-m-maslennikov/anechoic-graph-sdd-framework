import type { Page } from '@playwright/test';
import { graphQueryResponse } from './console-graph-mock';
import { matchesToolPath, toolReply, toolRequest } from './tool_rest_fixture';

function documentState(graph: boolean, refs: string[]) {
  const run = { status: 'success', query_id: 'q1', revision: 1 };
  const views = [{ id: 'v1', name: 'Source', sql:
    `SELECT reference FROM atoms${graph ? ' VIEW GRAPH' : ''}`, cursor_position: 0, revision: 1, result: run }];
  let active = 'v1';
  const state = () => ({ project_name: 'Fixture', workspace_id: 'test', active_view_id: active, views });
  const result = () => ({ query_id: 'q1', columns: [{ name: 'ref', type: 'VARCHAR', has_values: true }],
    rows: refs.map((ref) => [ref]), row_count: refs.length, offset: 0, page_size: 100, has_more: false });
  return { run, views, state, result,
    focus: (id: string) => { active = id; } };
}

export async function mockDocuments(page: Page, graph = false, refs =
  ['AN-S-1', 'AN-S-1@1']) {
  const requests: string[] = [];
  const { run, views, state, result, focus } = documentState(graph, refs);
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'query_run': value = graphQueryResponse(args.sql as string); break;
      case 'query_schema': value = { tables: [] }; break;
      case 'iwe_console_status': value = { mode: 'unavailable' }; break;
      case 'query_saved_list': case 'query_log_list': value = { items: [] }; break;
      case 'workspace_get': case 'workspace_open': value = state(); break;
      case 'view_fetch': {
        const grid = args.grid as { group_by?: unknown } | undefined;
        value = {
          ...result(), ...(Boolean(grid?.group_by) &&
            { groups: refs.map((ref) => ({ value: ref, count: 1 })) }),
        };
        break;
      }
      case 'view_focus': focus(args.view_id as string); value = state(); break;
      case 'view_create':
        const active = `v${views.length + 1}`; focus(active);
        views.push({ id: active, name: args.name as string, sql: '',
          cursor_position: 0, revision: 1, result: run });
        value = { ...state(), view_id: active }; break;
      case 'view_update': {
        const view = views.find((item) => item.id === args.view_id)!;
        view.sql = args.sql as string; view.revision++; value = view; break;
      }
      case 'view_run': value = { ...run,
        revision: views.find((item) => item.id === args.view_id)!.revision }; break;
      case 'iwe_console_atom_document': {
        const ref = args.ref_id as string; requests.push(ref);
        value = documentResponse(ref); break;
      }
      default: return route.fallback();
    }
    await route.fulfill({ json: toolReply(route, value) });
  });
  return requests;
}

function documentResponse(ref: string) {
  return { ref_id: 'AN-S-1', exact_ref: ref.includes('@') ?
    ref : 'AN-S-1@2', version: ref.includes('@') ? 1 : 2,
        status: 'Current', filename: ref.includes('@') ?
          'AN-S-1@1.md' : 'AN-S-1.md', body: 'Body AN-S-2',
        history: ref.includes('@') ? [] : [
          { ref_id: 'AN-S-1@1', version: 1, status:
            'Archived', filename: 'AN-S-1@1.md' },
          { ref_id: 'AN-S-1@3-ready', version: 3, status:
            'Ready', filename: 'AN-S-1@3-ready.md' },
          { ref_id: 'AN-S-1@4-draft', version: 4, status:
            'Draft', filename: 'AN-S-1@4-draft.md' },
        ], relations: [{ type: 'USES', ref_id: 'AN-S-2',
          direction: 'outgoing', derived: false }],
        contained: [{ ref_id: 'AN-T-5', filename: 'AN-T-5.md' }] };
}
