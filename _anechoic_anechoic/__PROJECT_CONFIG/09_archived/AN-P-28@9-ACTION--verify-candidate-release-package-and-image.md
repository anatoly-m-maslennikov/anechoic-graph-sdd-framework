---
atom_family: PROJECT_CONFIG
atom_id: AN-P-28
structure:
  container:
    component: C00
context:
  template: action
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Verify candidate release package and image

# Summary

Verify candidate release package and image

## Action

Verify candidate release package and image **means** the Action that performs one bound `closed_unit_gate`, `candidate_image_build`, or `candidate_image_canary` phase for the frozen local boundary.

## Scope

The `closed_unit_gate` phase binds the Version, active source identities and digests, Project Structure, settings, exact private compiled candidate, and declared Unit/source partition. It is not host Candidate E2E or the complete Release Gate. `candidate_image_build` and `candidate_image_canary` bind the exact staged package, runtime, compiled product, and `ca` payload after that Unit gate. Host-capable Candidate E2E is CA-O-182; CA-O-184 alone aggregates the complete Release Gate. These phases do not create another release Workflow.

## Details

A partial, cached, focused, stale, source-only, or unjournaled result is not proof. This Action never clears, copies, installs, publishes, or retries. Each actual Action Run is journaled once with its exact inputs and result.
