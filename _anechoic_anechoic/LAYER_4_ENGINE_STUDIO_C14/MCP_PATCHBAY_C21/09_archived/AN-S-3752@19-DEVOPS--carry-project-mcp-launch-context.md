---
atom_family: SPEC
atom_id: AN-S-3752
container:
  component: C21
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-11-09 17:00:18 +0400
---

## Summary

Carry Project MCP launch context

## Claim

### Prose Claim

The launcher **must** carry one explicit ProjectSelection record whose identity and selected bindings are sufficient to isolate the MCP Gateway and launcher state. The record carries the canonical host Project root, selected control root, Project identity, container path mapping and selected manifest, registry and query-source references.

The Codex hook's top-level project_root is an optional assertion for single-Project Tool calls and a required assertion for shared-Project Tool calls. Validate it against the carried ProjectSelection before Tool dispatch. A malformed or mismatched assertion produces a safe refusal with no native Tool execution, source effect or Journal effect. Remove the assertion envelope before a native Tool receives its own arguments. Prompt and Workflow wrappers retain their normal dispatch; initialize and tools/list are protocol operations, not Tool-call envelopes.

tools/list **must** advertise the top-level project_root input as optional for the single-Project service and required for the shared service, without mutating the native Tool descriptors or their input schemas. The advertisement describes the service boundary only; native Tool arguments remain unchanged.

Place launcher-owned Gateway context, hot-reload receipts, cache metadata, pending-launch evidence and the per-Project lock under the selected Project's installed runtime state in an identity-named namespace. Gateway and reload constructors consume the carried selection rather than scanning for a default control root or repository ancestor. A Carrier records safe identifiers and relative references, never credentials or an unselected Project's content.

This Carrier delivers no proxy, listener, worker, queue, Workflow request or Release transition. Shared delivery may serve multiple explicit Projects through one endpoint, but each request remains bound to its validated ProjectSelection.
