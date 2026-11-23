---
atom_family: SPEC
atom_id: AN-S-2440
container:
  component: C19
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Validate public-release request admission

# Summary

Validate public-release request admission

## Scope

one public-release request before execution.

## Claim

**the Operator** **must** verify that missing fields, unknown fields, bad digests, unsafe refs, malformed Run graph, stale preview, and absent or stale authorization all stop before a native binding is invoked.

## Details

Use a disposable Project and mock bindings. A valid preview alone is not execute success.
