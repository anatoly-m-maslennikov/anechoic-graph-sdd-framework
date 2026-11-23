---
atom_family: SPEC
atom_id: AN-S-34
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Preserve semantic revision and history through lifecycle dispatch

# Summary

Preserve semantic revision and history through lifecycle dispatch

## Scope

Result semantics at the dispatch boundary; native lifecycle Tools retain their own mutation mechanics.

## Claim

For every admitted result, the dispatcher **must** carry the native Tool's actual Version, Updated At, prior semantic Revision, replacement lineage, and effect evidence without fabricating a timestamp or history entry. A carrier-only/equivalent refinement uses the native Update rule; a semantic revision advances exactly once under its admitted class; Replace preserves predecessor/successor lineage; Change Status preserves prior state and records the actual current status model/revision used.

An actual no-op reports no accepted edit, timestamp refresh, Version advance, archive, or invented history. A rejected preflight reports no performed effect. A started operation with incomplete, failed, or partially verified effects reports each known effect and unknown remainder truthfully; it is not reported as a complete lifecycle success.

## Details

This contract does not define Journal storage or retry behavior; it provides the lifecycle result facts that the shared Run support records.
