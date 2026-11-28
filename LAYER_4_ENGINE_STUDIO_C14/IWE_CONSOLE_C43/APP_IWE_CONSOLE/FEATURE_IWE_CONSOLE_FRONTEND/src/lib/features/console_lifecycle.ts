import type { AtomDocumentData } from './console_document';
import { WorkbenchRequestError } from '../lib__shared';

type Call = (name: string, args: Record<string, unknown>) => Promise<unknown>;
type Relation = { type: string; ref_id: string };

type Artifact = { ref_id?: string; updated_at?: string };
type LifecycleResult = { artifact?: Artifact; savedDraft?: Artifact };

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(
    value) ? value as Record<string, unknown> : {};
}

function artifact(value: unknown): Artifact | undefined {
  const item = record(value);
  if (typeof item.ref_id !== 'string' &&
    typeof item.updated_at !== 'string') return undefined;
  return { ...(typeof item.ref_id === 'string' ? { ref_id: item.ref_id } : {}),
    ...(typeof item.updated_at === 'string' ?
      { updated_at: item.updated_at } : {}) };
}

export function lifecycleResult(value: unknown): LifecycleResult {
  if (!value || typeof value !== 'object' || Array.isArray(
    value)) throw new Error('Empty lifecycle response');
  const result = record(value);
  if (result.status === 'failed' ||
    result.status === 'blocked' || result.isError === true) {
    const details = Array.isArray(result.errors) ?
      result.errors.map(record) : [];
    const errors = details.map((error) => {
      return typeof error.message === 'string' ? error.message :
        typeof error.code === 'string' ? error.code : '';
    }).filter(Boolean).join('; ');
    const code = details.find((error) =>
      error.code === 'source_changed')?.code ?? details[0]?.code;
    throw new WorkbenchRequestError(errors || 'Lifecycle request failed',
      typeof code === 'string' ? code : undefined);
  }
  return { artifact: artifact(result.artifact),
    savedDraft: artifact(result.savedDraft) };
}

export function artifactRef(result: LifecycleResult): string {
  const item = result.savedDraft || result.artifact;
  if (!item?.ref_id) throw new Error(
    'Lifecycle response has no Atom reference');
  return item.ref_id;
}

export function availableStatuses(document: AtomDocumentData): string[] {
  const { ref_id, template, status } = document;
  const spec = ref_id.includes('-S-');
  const ticket = ref_id.includes('-T-');
  if (ticket && status.toLowerCase() !== 'draft' &&
    document.ticket_statuses !== undefined) return document.ticket_statuses;
  switch (status.toLowerCase()) {
    case 'draft': return spec ? ['ready',
      'active'] : ticket ? ['backlog'] : ['active'];
    case 'ready': return spec ? ['active'] : [];
    case 'backlog': return ticket ? ['in_queue'] : [];
    case 'active':
    case 'in_queue': {
      if (spec) return ['archived'];
      const queue = status.toLowerCase() === 'active' ? ['in_queue'] : [];
      if (template === 'task' || template === 'epic') return [
        ...queue, 'done', 'canceled'];
      if (['problem', 'question',
        'code_spec_mismatch', 'opportunity'].includes(
        template ?? '')) return [...queue, 'resolved', 'canceled'];
      return [];
    }
    default: return [];
  }
}

export class DraftSave {
  body: string;
  savedBody: string;
  removed: Relation[] = [];
  updatedAt: string | null | undefined;
  error = '';
  conflicted = false;
  saving = false;
  private timer: ReturnType<typeof setTimeout> | undefined;
  private pending: Promise<boolean> | undefined;
  private document: AtomDocumentData;
  private call: Call;
  private notify: () => void;
  constructor(document: AtomDocumentData, call: Call, notify: () => void) {
    this.document = document; this.call = call; this.notify = notify;
    this.body = this.savedBody = document.body;
    this.updatedAt = document.updated_at;
  }
  get dirty() { return this.body !== this.savedBody ||
    this.removed.length > 0; }
  edit(body: string) { this.body = body; this.schedule(); }
  remove(relation: Relation) {
    if (!this.removed.some((r) => r.type === relation.type &&
      r.ref_id === relation.ref_id)) this.removed.push(relation);
    this.schedule();
  }
  private schedule() {
    if (!this.conflicted) this.error = '';
    if (!this.dirty) { clearTimeout(this.timer); this.timer = undefined; }
    else if (!this.timer && !this.saving && !this.conflicted) this.timer =
      setTimeout(() => { this.timer = undefined; void this.save(); }, 5000);
    this.notify();
  }
  async save(): Promise<boolean> {
    clearTimeout(this.timer); this.timer = undefined;
    if (this.pending) return this.pending;
    if (!this.dirty) return true;
    if (this.conflicted) return false;
    const body = this.body;
    const removed = [...this.removed];
    this.error = ''; this.saving = true; this.notify();
    this.pending = (async () => {
      try {
        const changes: Record<string, unknown> = {};
        if (body !== this.savedBody) changes.body = body;
        if (removed.length) changes.removeRelations = removed;
        const result = lifecycleResult(
          await this.call('atom_lifecycle_update', {
          target: { ref_id: this.document.exact_ref,
            version: this.document.version }, changes,
          ...(this.updatedAt ? { expectedUpdatedAt: this.updatedAt } : {}),
        }));
        if (!result.artifact?.updated_at) throw new Error(
          'Save response has no updated timestamp');
        this.updatedAt = result.artifact.updated_at;
        this.savedBody = body;
        this.removed = this.removed.filter((r) => !removed.some((
          saved) => saved.type === r.type && saved.ref_id === r.ref_id));
        return true;
      } catch (error) {
        this.conflicted = error instanceof WorkbenchRequestError &&
          error.code === 'source_changed';
        this.error = error instanceof Error ? error.message : 'Save failed';
        return false;
      } finally {
        this.saving = false; this.pending = undefined; this.notify();
        if (!this.error && this.dirty) this.schedule();
      }
    })();
    return this.pending;
  }
  async flush(): Promise<boolean> {
    while (this.dirty || this.pending) if (!await this.save()) return false;
    return true;
  }
  discard() {
    clearTimeout(this.timer); this.timer = undefined;
    this.body = this.savedBody;
    this.removed = [];
    this.error = '';
    this.notify();
  }
  dispose() { clearTimeout(this.timer); }
}
