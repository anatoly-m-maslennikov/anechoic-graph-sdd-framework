---
atom_family: SPEC
atom_id: AN-S-3019
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:27.109259+00:00'
---
## Summary

Validate effective child allowances against applicable Policy

## Claim

### Prose Claim

A parent Spec Policy can select child Component Manifests. For each selected child, validate its effective `io_allowance`—after nearest-ancestor inheritance and any explicit child override—against every applicable Policy. A violation reports the direction, channel, Policy, explicit reason, authored allowance, and effective allowance, then preserves the authored value; validation does not silently narrow or rewrite it.

## Details

Acceptance: a child whose effective input and output channels satisfy all applicable Policies passes; an over-broad direction fails with the named channel and Policy and leaves the authored child allowance unchanged. Reject a check that validates only the inherited default, omits the explicit child override, or mutates the value while reporting the violation.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
