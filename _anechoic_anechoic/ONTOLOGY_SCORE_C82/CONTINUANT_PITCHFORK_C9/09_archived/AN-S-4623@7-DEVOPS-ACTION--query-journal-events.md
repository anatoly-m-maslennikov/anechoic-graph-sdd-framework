---
atom_family: SPEC
atom_id: AN-S-4623
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Query Journal Events

# Summary

Query Journal Events

## Operation

The Journal Event query Action **must** read one stable snapshot of the selected Project's canonical Events Journal, evaluate only its bounded literal filter grammar, and return Event IDs by default or only caller-selected Event fields or full Events on request.

## Details

The Action consumes the exact pre-dispatch sealed byte-prefix frontier. A
standalone Action captures that frontier before its own Run evidence.

The Action reuses CA-R-1850's one shared literal filter grammar. It neither writes Events nor creates a competing Journal, Projection, SQL interpreter, arbitrary-code evaluator, credential reader, mutation authority, or invented Run. It reports exact malformed, missing, duplicate, incomplete, changed-source, coverage, pagination, and filter diagnostics rather than skipping or passing them.
