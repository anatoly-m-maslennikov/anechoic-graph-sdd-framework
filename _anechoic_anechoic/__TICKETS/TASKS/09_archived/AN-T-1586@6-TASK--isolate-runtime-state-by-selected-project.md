---
atom_family: TKT
atom_id: AN-T-1586
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Isolate runtime state by selected Project

# Summary

Isolate runtime state by selected Project

## Objective

the AI Agent binds container naming, persistent state, **and** declared mounts **to** the selected Project identity.

## Details

- input: the shared selector **and** runtime state **and** Compose configuration under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/203_APPS/WORKFLOW_ORCHESTRATOR`, plus MCP reload storage **in** `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/204_MCP/hot_reload.py`.
- output: per-Project Compose **and** state namespaces that separate locks, transport metadata, credentials, queues, MCP reload receipts/pending/cache storage, **and** declared authority bindings; use the accepted mount boundary.
- verification: compare two selected Projects **in** one repository **and** two repositories; writing one instance's state leaves the other instance's state unchanged.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: shared selection-derived Compose, launcher **and** reload namespaces **and** the standalone endpoint-only mount declaration are implemented. 2 state/mount tests passed, including a left-only same-ID receipt leaving the other nested Project unchanged.

the Plan is **not** Done **if** ((two selected Projects share mutable runtime state) **or** (the resulting mounts exceed the accepted Project boundary) **or** (the namespace/isolation tests fail)).
