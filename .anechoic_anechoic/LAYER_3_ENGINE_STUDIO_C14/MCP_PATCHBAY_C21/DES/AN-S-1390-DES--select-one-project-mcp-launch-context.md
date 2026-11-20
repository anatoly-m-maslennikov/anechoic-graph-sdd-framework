---
identity:
  atom_id: AN-S-1390
context:
  container:
    component: C21
  tier: 3
  lens: DES
state:
  status: active
  version: 18
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

select one Project MCP launch context

## Claim

### Prose Claim

the Project MCP launcher **must** resolve **=1** safe, explicit Project context from its Project-root path and optional control-root selector, or refuse unchanged without selecting, mounting, or affecting another Project.

## Details

### Project selection and binding

- The default is `--project-root repo`, where `repo` is the declared Project root. An explicit root must be an existing canonical directory with exactly one valid local control root; an explicit `--control-root .anechoic_name` must be one direct normalized non-symlink child with no traversal. Without it, enumerate only direct `.anechoic_*` candidates and require exactly one valid Project Settings/Structure. Refuse zero/multiple, outside-root, invalid, or unreadable candidates; never choose a sibling, parent, nested Project, historical default, or Git ancestor.
- `project_identity = sha256(canonical_project_root + NUL + selected_control_root_relative_path)` is computed before `/project` translation and stays the selected-instance identity. Different roots under one Git repository remain distinct even when names, Engine sources, or fingerprints match.
- The immutable selection carries canonical host root, selected control root, container mapping, and exact Project-local manifest, registry, and query-source bindings. Gateway, reload, registry, and query-source operations consume only that context; they never fall back to a process-global root or another Project. State, locks, receipts, caches, and pending launches are namespaced by this identity; foreign state is neither reusable nor a cleanup target.
- An explicitly selected canonical Project may be nested below the configured host projects-root mount when local checks pass; eager discovery remains bounded to direct children. Shared per-request mode may serve multiple explicit Projects through one endpoint under `CA-R-2008` and is not a global one-Project restriction.

### Project selection procedure

1. Canonicalize the declared root and `--project-root`; reject missing, non-directory, escaping, or symlink-substituted paths. Do not search ambient CWD or Git ancestors.
2. Normalize `--control-root` as a direct relative child when supplied; otherwise enumerate direct `.anechoic_*` candidates, require exactly one valid candidate, and validate Settings/Structure. A local `.git` is not required.
3. Build `ProjectSelection` once with canonical host path, `/project` mapping, identity, and selected control-root-relative path; no later component may replace the root.
4. Bind only the selected manifest, active registry, and admitted query source. A missing, changed, foreign, duplicate, or unadmitted binding stops before image inspection.
5. Derive the identity-named installed-runtime namespace and per-Project lock; store only that selection's receipts, caches, pending evidence, and safe metadata. Do not read, reuse, delete, or merge a sibling namespace.
6. Return the immutable selection or a structured refusal with selector class and no substituted path; start no container, listener, worker, queue, Workflow, Tool call, or Release action.
7. Permit an explicitly selected nested Project when its local checks pass, while keeping eager mount discovery direct-child bounded. Shared per-request selection may serve multiple explicit Projects; when host/container roots are identical, carry the same absolute root without translation.

### Immutable launch context

Carry one explicit `ProjectSelection` whose identity and bindings isolate MCP Gateway and launcher state: canonical host root, selected control root, identity, container mapping, manifest, registry, and query-source references. The Codex hook's top-level `project_root` is optional for single-Project Tool calls and required for shared calls; validate it against the selection before dispatch, refuse malformed/mismatched assertions, and remove the envelope before native Tool arguments. Initialize and tools/list are protocol operations, not Tool-call envelopes; Prompt and Workflow wrappers retain normal dispatch.

tools/list advertises `project_root` as optional for single-Project and required for shared service without mutating native descriptors or schemas. Place Gateway context, reload receipts, cache metadata, pending evidence, and the lock under the identity-named installed state; record safe identifiers and relative references, never credentials or unselected content. Shared delivery may serve multiple explicit Projects through one endpoint, but each request remains bound to its validated selection and this carrier creates no proxy, worker, queue, Workflow request, or Release transition.
