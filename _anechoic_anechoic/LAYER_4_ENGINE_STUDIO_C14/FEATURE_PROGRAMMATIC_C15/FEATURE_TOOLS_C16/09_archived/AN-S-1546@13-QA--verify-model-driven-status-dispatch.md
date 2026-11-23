---
atom_family: SPEC
atom_id: AN-S-1546
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Verify model-driven status dispatch

# Summary

Verify model-driven status dispatch

## Scope

Current status-model resolution for one selected Atom.

## Claim

Use fixtures with distinct admitted Content Role status models. Verify Create accepts each requested model-admitted initial Status and Tool-side Change Status and Archive derive only the actual carried Role and optional Type's current authoritative model, exact source/revision and destination mapping. Verify a manually created Draft with no retained history can perform an otherwise admitted explicit Status update. A request with caller-forged Role/Type/model identity, unavailable, ambiguous, stale, mismatched or unadmitted authority/status is rejected with its diagnostic and no write. Verify that no fixed status list makes an otherwise valid model-specific request succeed or fail, and that Journal absence or append failure does not change an observed admitted Status effect or authorize replay.

## Details

### Acceptance criteria

Each result identifies the resolved model source/revision, operation and authoritative destination decision. Prove Role/Type precedence, exact status casing, source-currentness, destination creation and collision handling, and same-status no-op. Rejected and preview cases leave all Carriers and history unchanged.
