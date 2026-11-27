

export interface OperationCaller {
  call<T>(name: string, arguments_: Record<string, unknown>): Promise<T>;
}

export class WorkbenchRequestError extends Error {
  constructor(message: string, readonly code?: string) { super(message); }
}

export function toolFailure(value: unknown, message?: string, code?: string): WorkbenchRequestError {
  const result = value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
  const diagnostics = (result.outcome === 'failed' || result.outcome === 'rejected')
    && Array.isArray(result.diagnostics) && result.diagnostics.every((item: unknown) => typeof item === 'string')
    ? result.diagnostics as string[] : [];
  const diagnostic = diagnostics.find((item) => item.length > 0);
  const diagnosticCode = diagnostic?.match(/^([a-z][a-z0-9_]*)(?:: |$)/)?.[1];
  return new WorkbenchRequestError(message || diagnostic || 'Invalid Workbench tool error response.', code || diagnosticCode);
}

const HTTP_ROUTES: Record<string, string> = {
  query_rebuild: 'rebuild', query_run: 'run', query_check: 'check', query_page: 'page', query_schema: 'schema',
  iwe_console_status: 'status', workbench_status: 'status', query_load: 'load', query_saved_list: 'saved-list',
};

const INTERFACE_OPERATIONS = new Set([
  'iwe_console_atom_document', 'atom_lifecycle_create_draft', 'atom_lifecycle_update',
  'atom_lifecycle_promote_draft', 'atom_lifecycle_change_status',
  'workspace_open', 'workspace_list', 'workspace_get', 'view_create', 'view_list', 'view_get',
  'view_duplicate', 'view_update', 'view_run', 'view_check', 'view_fetch', 'view_focus', 'view_rename',
  'view_remove', 'query_log_list', 'query_log_get',
]);

export class HttpOperationCaller implements OperationCaller {
  constructor(private readonly base: string, private readonly projectRoot: string | null) {}

  call<T>(name: string, arguments_: Record<string, unknown>): Promise<T> {
    if (INTERFACE_OPERATIONS.has(name) || (name === 'view_save' && 'workspace_id' in arguments_)) {
      return this.post('interface', { operation: name, arguments: arguments_ });
    }
    if (name === 'view_save') return this.post('view-save', arguments_);
    const path = HTTP_ROUTES[name];
    if (!path) return Promise.reject(new Error(`Unsupported Workbench operation: ${name}`));
    return this.post(path, arguments_);
  }

  private async post<T>(path: string, body: Record<string, unknown>): Promise<T> {
    const apiBase = this.base.replace(/^\/anechoic\/(?:iwe-console|workbench)\/([^/]+)$/, '/anechoic/$1/api');
    const response = await fetch(`${apiBase}/${path}`, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify(this.projectRoot ? { ...body, project_root: this.projectRoot } : body),
    });
    let value: unknown;
    try { value = await response.json(); }
    catch { throw new Error('Invalid Workbench response: expected JSON.'); }
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid Workbench response: expected an object.');
    if (!response.ok) {
      const details = value as Record<string, unknown>;
      if (typeof details.error !== 'string') throw new Error('Invalid Workbench error response.');
      throw toolFailure(details.tool_result, details.error, typeof details.code === 'string' ? details.code : undefined);
    }
    return value as T;
  }
}
