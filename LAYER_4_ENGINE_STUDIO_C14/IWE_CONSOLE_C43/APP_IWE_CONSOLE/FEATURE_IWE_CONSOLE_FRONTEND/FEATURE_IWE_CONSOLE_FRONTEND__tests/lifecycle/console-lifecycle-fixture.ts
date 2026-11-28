import { expect, test, type Locator, type Page, type Request,
  type Response } from '@playwright/test';
import type { Effect } from '../unit/support/support__shared';
import { isToolCall, matchesToolPath, toolReply,
  toolRequest } from '../unit/support/support__shared';

const authoredRelation = { type: 'IS_SOLUTION_FOR', ref_id: 'AN-S-1' };
const readOnlyRelations = [
  { type: 'CONTAINED_BY', ref_id: 'C00',
    direction: 'outgoing', derived: false },
  { type: 'DERIVED', ref_id: 'AN-S-2', direction: 'outgoing', derived: true },
  { type: 'INCOMING', ref_id: 'AN-S-3',
    direction: 'incoming', derived: false },
];

function lifecycleTable(ref: string, inline?: boolean) {
  const run = { query_id: 'current', revision: 1, status: 'success' };
  const active = { id: 'view', name: 'Active View', sql:
    'SELECT reference FROM atoms' + (inline ? ' VIEW DOCUMENT' : ''),
    revision: 1, cursor_position: 0, result: run };
  const other = { id: 'other', name: 'Other View',
    sql: 'SELECT 2', revision: 1, cursor_position: 0 };
  const workspace = { workspace_id: 'test', project_name: 'Test',
    active_view_id: active.id, views: inline ? [active, other] : [active] };
  const result = { query_id: run.query_id, columns:
    [{ name: 'reference', type: 'VARCHAR' }],
    rows: [[ref]], row_count: 1, offset: 0, page_size: 100, has_more: false };
  return { workspace, result, other };
}

function lifecycleDocuments(family: string, hasDraft:
  boolean, highest: number, ticketStatuses?: string[]) {
  const stable = `AN-${family}-1`;
  const draftVersion = hasDraft ? 1 : highest + 1;
  const exact = `${stable}@${draftVersion}-draft`;
  const publishStatus = family === 'S' ? 'ready' : 'backlog';
  let body = '## Summary\n\nCreated\n'; let stamp = 'one';
    let removed = false; let currentStatus = publishStatus;
  const history = [
    { ref_id: stable, version: 1, status:
      publishStatus, filename: 'current.md' },
    ...(highest > 1 ? [{ ref_id: `${stable}@${highest}`, version:
      highest, status: 'archived', filename: 'archived.md' }] : []),
    { ref_id: exact, version: draftVersion,
      status: 'draft', filename: 'draft.md' },
  ].filter((revision) => hasDraft || revision.status !== 'draft');
  const document = (ref: string) => ({ ref_id:
    stable, exact_ref: ref === exact ? exact : stable,
    version: ref === exact ? draftVersion :
      1, status: ref === exact ? 'draft' :
      currentStatus, filename: ref === exact ? 'draft.md' : 'current.md',
    ...(ticketStatuses && ref !== exact ? {
      ticket_statuses: ticketStatuses } : {}),
    authored_relations: ref === exact && !removed ? [authoredRelation] : [],
    body, updated_at: stamp, template: family === 'S' ?
      'axiom' : 'task', history, contained: [],
    relations: removed ? readOnlyRelations : [
      { ...authoredRelation, direction: 'outgoing',
        derived: false }, ...readOnlyRelations,
    ] });
  function save(changes: { body?: string;
    removeRelations?: unknown[] }, refuse?: boolean) {
    if (refuse) {
      body = '## Summary\n\nCreated\n\nChanged on server\n'; stamp = 'newer';
      return { status: 'failed', errors: [{ code: 'source_changed', message:
        'Draft updated_at does not match the expected timestamp.' }] };
    }
    if (changes.body) body = changes.body;
    if (changes.removeRelations) removed = true;
    stamp = 'two'; return { status: 'completed',
      artifact: { ref_id: exact, updated_at: stamp } };
  }
  return { stable, exact, draftVersion, publishStatus, document, save,
    changeStatus(status: string) { currentStatus = status; } };
}

function lifecycleState(family: string, hasDraft: boolean,
  ticketStatuses: string[] | undefined,
  options: { inline?: boolean; highestVersion?: number }) {
  const docs = lifecycleDocuments(family, hasDraft,
    options.highestVersion ?? 1, ticketStatuses);
  const { stable, exact, draftVersion, publishStatus } = docs;
  const table = lifecycleTable(
    options.inline ? exact : stable, options.inline);
  return { docs, stable, exact, draftVersion, publishStatus, table };
}

function lifecycleSaver(docs: ReturnType<typeof lifecycleDocuments>,
  options: { waitForFirstSave?: Promise<void>; refuseSave?: boolean;
    refuseSecondSave?: boolean }) {
  let saves = 0;
  return async (args: Record<string, unknown>) => {
    const save = ++saves;
    if (save === 1 && options.waitForFirstSave) await options.waitForFirstSave;
    return docs.save(args.changes as Parameters<typeof docs.save>[0],
      options.refuseSave || (save === 2 && options.refuseSecondSave));
  };
}

export async function lifecycleFixture(page: Page,
  family = 'T', hasDraft = true, ticketStatuses?: string[],
  options: { inline?: boolean; refuseSave?: boolean;
    refuseSecondSave?: boolean; waitForFirstSave?: Promise<void>;
    refuseCreate?: boolean; highestVersion?: number } = {}) {
  const calls: { operation: string; arguments: any; reply: any }[] = [];
  const { docs, stable, exact, draftVersion, publishStatus, table } =
    lifecycleState(family, hasDraft, ticketStatuses, options);
  const save = lifecycleSaver(docs, options);
  await page.route(matchesToolPath, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback();
    const { name, arguments: args } = toolRequest(route); let result: unknown;
    switch (name) {
      case 'query_schema': return route.fulfill(
        { json: toolReply(route, { tables: {} }) });
      case 'iwe_console_status': return route.fulfill(
        { json: toolReply(route, { mode: 'unavailable' }) });
      case 'query_saved_list': return route.fulfill(
        { json: toolReply(route, { items: [] }) });
      case 'workspace_open': case 'workspace_get':
        result = table.workspace; break;
      case 'view_rename': table.other.name =
        args.name as string; result = { ...table.other }; break;
      case 'view_focus': result = { workspace_id: table.workspace.workspace_id,
        active_view_id: args.view_id }; break;
      case 'view_fetch': result = table.result; break;
      case 'iwe_console_atom_document': result =
        docs.document(args.ref_id as string); break;
      case 'atom_lifecycle_create_draft': result = options.refuseCreate ?
        { status: 'failed', errors: [{ message: 'fixture stop' }] }
        : { status: 'completed', savedDraft: { ref_id:
          exact, version: draftVersion } }; break;
      case 'atom_lifecycle_update': result = await save(args); break;
      case 'atom_lifecycle_promote_draft': expect(args.targetStatus).toBe(publishStatus);
        result = { status: 'completed', artifact: { ref_id: stable } }; break;
      case 'atom_lifecycle_change_status': expect(args.targetStatus).toBe(ticketStatuses ? ticketStatuses[1] : family === 'S' ? 'active' :
        'in_queue'); docs.changeStatus(args.targetStatus as string); result = { status: 'completed', artifact: { ref_id: stable } }; break;
      case 'query_log_list': result = { items: [] }; break;
      default: return route.fallback();
    }
    calls.push({ operation: name, arguments: args, reply: result });
    return route.fulfill({ json: toolReply(route, result) });
  });
  return { calls, stable, exact };
}

function requestedTool(request: Request): string | undefined {
  if (!isToolCall(request)) return;
  return request.postDataJSON().name;
}

async function observeReply(operation: string,
  response: Response): Promise<Effect | undefined> {
  const target = `C21.${operation}`;
  if (!response.ok()) return [target, 'failed'];
  const { result, error } = await response.json();
  const value = result?.value;
  if (error || value?.status === 'failed') return [target, 'failed'];
  if (value?.status === 'completed' || (
    operation === 'view_rename' && value?.id && value.name)) {
    return [target, 'succeeded'];
  }
}

type Observation = Effect | Promise<Effect | undefined>;

export async function attachDraftGuardTrace(output: string, effects: Effect[],
  values: Record<string, Record<string, unknown>>) {
  await test.info().attach('draft-guard-trace', {
    contentType: 'application/json',
    body: JSON.stringify({
      action: 'guard_draft_editor', output, effects,
      events: Object.entries(values).map(([event, detail]) => ({ event, detail })),
    }),
  });
}

export async function observeLifecycle(page: Page, trackSavePhase = false) {
  const observations: Observation[] = [];
  const savePhases = new Map<Request, string>();
  page.on('request', request => {
    const operation = requestedTool(request);
    if (!operation) return;
    const effect: Effect = [`C21.${operation}`, 'requested'];
    if (trackSavePhase && operation === 'atom_lifecycle_update') {
      const phase = savePhases.size === 0 ? 'pending' : 'latest';
      savePhases.set(request, phase);
      effect[2] = { phase };
    }
    observations.push(effect);
  });
  page.on('response', response => {
    const operation = requestedTool(response.request());
    if (operation && ['atom_lifecycle_create_draft',
      'atom_lifecycle_update', 'view_rename'].includes(operation)) {
      const phase = savePhases.get(response.request());
      observations.push(observeReply(operation, response).then(effect => {
        if (effect && phase) effect[2] = { phase };
        return effect;
      }));
    }
  });
  await page.exposeFunction('reportLifecycleEffect', (
    effect: Effect) => { observations.push(effect); });
  return async () => (await Promise.all(observations)).filter(
    (effect): effect is Effect => !!effect);
}

type LifecycleWindow = typeof window & {
  reportLifecycleEffect(effect: Effect): Promise<void> };

export async function watchAppearance(page: Page,
  selector: string, effect: Effect, text?: string) {
  await page.evaluate(({ selector, effect, text }) => {
    const observer = new MutationObserver(() => {
      const shown = Array.from(document.querySelectorAll(selector)).some(
        element => text === undefined || element.textContent?.trim() === text,
      );
      if (!shown) return;
      observer.disconnect();
      void (window as LifecycleWindow).reportLifecycleEffect(effect);
    });
    observer.observe(document.body, { childList:
      true, characterData: true, subtree: true });
  }, { selector, effect, text });
}

export async function watchDraft(body: Locator) {
  await body.evaluate(editor => {
    const section = editor.closest('section')!;
    const report = (window as LifecycleWindow).reportLifecycleEffect;
    let retained = false;
    const observer = new MutationObserver(() => {
      const status = section.querySelector(':scope > span')?.textContent;
      if (!editor.isConnected) {
        observer.disconnect();
        void report(['C46.draft_editor', 'unmounted',
          { dirty: status !== 'Saved' }]);
      } else if (!retained && section.querySelector('[role="alert"]')) {
        retained = true;
        void report(['C46.draft_editor', 'retained',
          { dirty: status === 'Unsaved changes' }]);
      }
    });
    observer.observe(document.body, { childList:
      true, characterData: true, subtree: true });
  });
}
