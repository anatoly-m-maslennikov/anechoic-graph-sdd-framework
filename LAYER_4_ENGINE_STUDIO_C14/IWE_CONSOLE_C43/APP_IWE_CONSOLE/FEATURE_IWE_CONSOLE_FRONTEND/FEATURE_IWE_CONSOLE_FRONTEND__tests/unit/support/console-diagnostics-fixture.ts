import type { Page, Route } from '@playwright/test';
import { matchesToolPath, toolReply, toolRequest } from './tool_rest_fixture';

export function refuseRebuild(route: Route) {
  const message = 'Rebuild refused by fixture';
  return route.fulfill({ json: {
    error: { code: 'rebuild_failed', message, scope: 'tool',
      tool_result: { outcome: 'failed',
        diagnostics: [`rebuild_failed: ${message}`] } },
    project: toolReply(route, null).project,
  } });
}

export async function diagnosticsFixture(page: Page) {
  const targets: string[] = [];
  const statusRequests: Record<string, unknown>[] = [];
  let unhealthy = false;
  const workspace = { workspace_id: 'test', project_name: 'Fixture',
    active_view_id: 'v1', views: [{ id: 'v1', name: 'View 1',
      sql: 'SELECT 1', cursor_position: 0, revision: 1 }] };
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route);
    let value: unknown;
    switch (name) {
      case 'iwe_console_status':
        statusRequests.push(args);
        value = unhealthy
          ? { mode: 'unavailable', health: { state: 'degraded' },
            last_synced_at: null, archive: { state: 'failed' },
            ingestion_issues: [{ atom_ref: 'AN-S-1', message: 'Bad source' }] }
          : { mode: 'live_index', health: { state: 'ready' },
            last_synced_at: '2026-01-01T00:00:00Z',
            archive: { state: 'ready' }, ingestion_issues: [] };
        break;
      case 'query_rebuild':
        targets.push(args.target as string);
        if (args.target === 'all') return refuseRebuild(route);
        unhealthy = true; value = { outcome: 'completed' }; break;
      case 'workspace_open': case 'workspace_get': value = workspace; break;
      case 'query_schema': value = { tables: [] }; break;
      case 'query_saved_list': case 'query_log_list':
        value = { items: [] }; break;
      default: return route.fallback();
    }
    return route.fulfill({ json: toolReply(route, value) });
  });
  return { targets, statusRequests };
}
