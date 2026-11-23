---
atom_family: SPEC
atom_id: AN-S-3726
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Refresh only accepted selected source pins

# Summary

Refresh only accepted selected source pins

## Scope

the exact admitted selected-source revision refresh under the current Epic.

## Claim

the selected binding Projection **must** support an explicitly authorized refresh of the exact source revision registered by CA-D-588-MCP-DELIVERY--register-the-prepared-successor-binding-refresh, while preserving its admitted capability identities and graph.

## Details

- the registered source revision is authority; the refreshed binding is derived evidence, not new authority.
- preserve **all** route identities, order, Steps, Actions, native calls, edges, query admissions and registry identity. **only** the registered version and digest occurrences and resulting derived digests change.
- retain exact current Operator authorization, source-currentness checks, publication intent, readback and Journal completion. a pending recording is not completed publication.
- unknown revisions, changes to topology or capability admission remain outside this refresh.

