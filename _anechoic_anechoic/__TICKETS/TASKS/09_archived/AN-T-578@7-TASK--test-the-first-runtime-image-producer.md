---
atom_family: TKT
atom_id: AN-T-578
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 10:08:20 +0400
---
## Summary

Test the first runtime image producer

# Summary

Test the first runtime image producer

## Objective

Create deterministic golden tests for the private bootstrap image producer and proof reader.

## Details

Own tests/test_bootstrap_image.py and its bounded fixtures. Cover complete package/command/canary proof, altered context/output/labels, missing/failed commands, immutable-ID mismatch, and no runtime/Skill/selector publication. Expected bounded effort: <=15 minutes; decompose further if necessary.

## Definition of Done

The owned source or implementation is independently accepted and its real verification result is saved. Source or mock proof alone does not close actual first-install or Release gates.

## Result

Twelve mocked command/receipt golden tests passed, including fixed argv, immutable image/canary binding, byte tamper refusal, retained test-double origin and executable-mode preservation.

Saved implementation: b790a3fd0. This is scoped source and fixture verification, not an actual complete Release or Framework installation. P1739 remains Active.
