import type { Page } from '@playwright/test';
import { toolReply, toolRequest } from './tool_rest_fixture';

const rows = (values: unknown[][], column = 'value') => ({
  sql: '', query_id: 'q1', columns: [{ name: column, type:
  'VARCHAR' }], rows: values, row_count: values.length,
    column_count: 1, offset: 0, page_size: 100, has_more: false });
const relations = [['AN-S-1', 'AN-S-2', 'uses'], ['AN-S-2', 'AN-S-3',
  'uses'], ['AN-S-1', 'AN-S-4', 'other'], ['AN-S-3', 'AN-S-1', 'cycle']];

export function graphQueryResponse(sql: string) {
  if (sql.includes('SELECT DISTINCT relation_type')) return rows(
    [['cycle'], ['other'], ['uses']]);
  if (sql.includes('FROM relations')) {
    const types = sql.match(/relation_type IN \(([^)]*)\)/)?.[1] ?? '';
    const refs = sql.match(/source_ref IN \(([^)]*)\)/)?.[1] ?? '';
    return rows(relations.filter(([a, b, t]) => types.includes(
      `'${t}'`) && (refs.includes(`'${a}'`) || refs.includes(`'${b}'`))));
  }
  if (sql.includes('FROM architecture_package_bindings')) {
    if (!sql.includes('b.atom_ref = s.exact_ref') ||
      !sql.includes('c.ref = s.exact_ref')) {
      throw Error('Graph did not join Spec Bindings by exact revision');
    }
    return rows([['package:p', 'AN-S-1',
      'Package'], ['C01', 'AN-S-1', 'Component']]);
  }
  if (sql.includes('SELECT exact_ref, reference FROM native_references')) {
    return rows([['AN-S-1@1', 'AN-S-1@1'], ['AN-S-1@2', 'AN-S-1']]
      .filter(([ref]) => sql.includes(`'${ref}'`)));
  }
  if (sql.includes('FROM import_nodes')) return rows([['module:a',
    'module', 'a.py'], ['module:b', 'module', 'b.py']]);
  if (sql.includes('FROM import_edges')) {
    if (!sql.includes("e.occurrence_key IN ('occ:1')")) throw Error(
      'Import query did not use result occurrences');
    return rows([['module:a', 'module:b', true]]);
  }
  throw Error(`Unexpected graph SQL: ${sql}`);
}

export async function mockGraph(page: Page, view: string, layout =
  'vertical', query?: string, seed = 'AN-S-1', otherRef?: string) {
  const graphSql = seed.includes('@') ?
    'SELECT exact_ref FROM native_references' : 'SELECT reference FROM atoms';
  const sql = query ?? (view === 'graph' ?
    `${graphSql} VIEW GRAPH ${layout.toUpperCase()}` :
    view === 'structure' ?
      'SELECT * FROM mrt_project_structure VIEW STRUCTURE' :
      `SELECT * FROM import_edges VIEW IMPORTS ${layout.toUpperCase()}`);
  const run = { status: 'success', query_id: 'q1', revision: 1 };
  const item = { id: 'v1', name: 'Graph', sql,
    cursor_position: 0, revision: 1, result: run };
  const state = { project_name: 'Fixture', workspace_id:
    'graph-test', active_view_id: 'v1', views: [item] };
  await page.route('**/tools', async route => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'query_run': value = graphQueryResponse(args.sql as string); break;
      case 'query_schema': value = { tables: [] }; break;
      case 'iwe_console_status': value = { mode: 'unavailable' }; break;
      case 'query_saved_list': case 'query_log_list': value = { items: [] }; break;
      case 'workspace_open': case 'workspace_get': value = state; break;
      case 'view_fetch':
        value = otherRef ? {
          ...rows([[seed, otherRef]], 'ref'),
          columns: ['ref', 'other_ref'].map(name => ({ name, type: 'VARCHAR' })),
          column_count: 2,
        } : view === 'structure' ? structureResult() :
          view === 'graph' ? rows([[seed]], 'ref') : view === 'imports' ?
            rows([['occ:1']], 'occurrence_key') : rows([['AN-S-1']], 'ref');
        break;
      case 'iwe_console_atom_document': value = { ref_id:
        args.ref_id, exact_ref: args.ref_id, version: 1, status: 'Current',
        filename: `${args.ref_id}.md`, body: 'Fixture document',
        history: [], relations: [], contained: [] }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, value) });
  });
}

function structureResult() {
  const value = rows([['C01', '', 'Component', 'Component One',
    'Purpose AN-S-1@2', 'AN-S-1@2', 'AN-S-2@9'],
    ['CS1', 'C01', 'Component Seed', 'Seed One',
      'Seed purpose', 'AN-S-3@1', 'AN-S-3@1']]);
  value.columns = ['id', 'parent', 'kind', 'name', 'purpose',
    'manifest', 'solutions'].map(name => ({ name, type: 'VARCHAR' }));
  value.column_count = value.columns.length;
  return value;
}
