import type { QueryPageCore } from './query_run.generated';

type PageColumn = QueryPageCore['columns'][number];
export type Column = Omit<PageColumn, 'has_values'> &
  Partial<Pick<PageColumn, 'has_values'>>;

export type SavedIdentity = {
  saved_query_id: string;
  saved_query_url: string;
  kind: 'query' | 'view';
  sql: string;
  name?: string;
};

export type QueryResult = Omit<QueryPageCore, 'columns'> & {
  sql: string;
  columns: Column[];
  rows: unknown[][];
  row_count: number;
  column_count: number;
  offset: number;
  page_size: number;
  has_more: boolean;
  filtered_row_count?: number;
  source_row_count?: number;
  groups?: Array<{ value: unknown; count: number }>;
  outcome?: 'partial';
  save_error?: string;
  query_log_error?: string;
  saved_query_id?: string;
  saved_query_url?: string;
  kind?: 'query';
  name?: string;
};

export type GridSort = { column: number; direction: 'asc' | 'desc' };
export type GridFilter = { column: number; operator: 'contains'; value:
  string };
export type GridState = { sort: GridSort[]; filters: GridFilter[]; group_by?:
  GridSort };
export type ResultDisplayPreferences = {
  rowSizing: 'adaptive' | 'fixed';
  fixedPageSize: number;
  content: 'limited' | 'full';
  contentLimit: number;
};

export type CheckResult = { valid: boolean; row_count: number; column_count:
  number };
export type Schema = { tables: Record<string, Array<{ name: string; type:
  string; values?: string[] }>> };
export type SavedItem = {
  saved_query_id: string;
  saved_query_url: string;
  kind: 'query' | 'view';
  preview: string;
  saved_at: string;
  name?: string;
};

export type ViewResult = {
  status: 'success' | 'failed';
  query_id: string | null;
  row_count?: number | null;
  column_count?: number | null;
  error?: string | null;
};

export type WorkspaceView = {
  id: string;
  sql: string;
  name?: string;
  revision: number;
  cursor_position: number;
  result?: ViewResult;
};

export type WorkspaceState = {
  workspace_id?: string;
  active_view_id?: string;
  views: WorkspaceView[];
  project_name?: string;
};

export type ViewRunResponse = ViewResult & {
  workspace_id: string;
  view_id: string;
  revision: number;
  saved_query_id?: string;
  saved_query_url?: string;
  save_error?: string;
  query_log_error?: string;
};

export type QueryLogItem = {
  log_id: string;
  at: string;
  sql: string;
  outcome: 'success' | 'failed';
  error?: string | null;
  row_count?: number | null;
  column_count?: number | null;
};

export type SourceSyncStatus = { mode?: 'startup_snapshot' | 'live_index' |
  'unavailable'; syncing?: boolean; last_synced_at?: string | null;
  health?: { state: 'ready' | 'pending' | 'degraded' | 'unavailable'; error?:
    { message?: string } };
  watcher_queue_depth?: number | null; last_run_state?: string | null;
  indexed_atom_count?: number; ingestion_issue_count?: number;
  worker_runs?: { active: Array<{ kind: string; status: string }>;
    latest: Array<{ kind: string; status: string }> };
  archive?: { state?: string }; ingestion_issues?: Array<{ atom_ref?:
    string; message?: string; code?: string; relative_path?: string }>;
};

export type Command = { id: string; label: string; shortcut?:
  string; enabled: boolean; run: () => void };
export type PreferenceCommand = { id: string; label: string; run: () => void };
