import { TOOL_REST_PATH } from './query_run.generated';

export interface OperationCaller {
  call<T>(name: string, arguments_: Record<string, unknown>): Promise<T>;
}

export class WorkbenchRequestError extends Error {
  constructor(message: string, readonly code?: string) { super(message); }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function toolFailure(value: unknown, message?
  : string, code?: string): WorkbenchRequestError {
  const result = isRecord(value) ? value : {};
  const diagnostics = (result.outcome === 'failed' ||
    result.outcome === 'rejected')
    && Array.isArray(result.diagnostics) && result.diagnostics.every(
      (item: unknown) => typeof item === 'string')
    ? result.diagnostics as string[] : [];
  const diagnostic = diagnostics.find((item) => item.length > 0);
  const diagnosticCode = diagnostic?.match(/^([a-z][a-z0-9_]*)(?:: |$)/)?.[1];
  return new WorkbenchRequestError(message || diagnostic ||
    'Invalid Workbench tool error response.', code || diagnosticCode);
}

export class HttpOperationCaller implements OperationCaller {
  constructor(private readonly projectInstance: string | undefined,
    private readonly projectRoot: string | null) {}

  async call<T>(name: string, arguments_: Record<string, unknown>): Promise<T> {
    if (!this.projectInstance || !/^[0-9a-f]{64}$/.test(this.projectInstance)) {
      throw new Error('The Console page has no valid Project instance.');
    }
    const response = await fetch(TOOL_REST_PATH, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'X-Anechoic-Project-Instance': this.projectInstance,
      },
      body: JSON.stringify({
        name,
        arguments: this.projectRoot ?
          { ...arguments_, project_root: this.projectRoot } : arguments_,
        session_id: null,
        public_base_url: null,
      }),
    });
    let envelope: unknown;
    try { envelope = await response.json(); }
    catch { throw new Error('Invalid Workbench response: expected JSON.'); }
    if (!isRecord(envelope)) throw new Error(
      'Invalid Workbench response: expected an object.');
    const { error, result, project } = envelope;
    if (!response.ok || 'error' in envelope) {
      if (!isRecord(error) || typeof error.message !== 'string' ||
          typeof error.code !== 'string' ||
          (error.scope !== 'project' && error.scope !== 'tool')) {
        throw new Error('Invalid Workbench error response.');
      }
      throw toolFailure(error.tool_result, error.message, error.code);
    }
    if (!isRecord(result) || Object.keys(result).length !== 2 ||
        !isRecord(result.value) ||
        (result.text !== null && typeof result.text !== 'string')) {
      throw new Error('Invalid Workbench response: expected a Tool result.');
    }
    if (!isRecord(project) || project.instance_id !== this.projectInstance) {
      throw new WorkbenchRequestError(
        'The API receipt does not identify the selected Project.',
        'project_receipt_mismatch');
    }
    return result.value as T;
  }
}
