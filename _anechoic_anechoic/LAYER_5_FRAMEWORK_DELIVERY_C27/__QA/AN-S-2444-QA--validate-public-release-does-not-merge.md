---
atom_family: SPEC
atom_id: AN-S-2444
structure:
  container:
    component: C27
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Validate public release does not merge

## Scope

one public-release effect declaration.

## Claim

### Prose Claim

**the Operator** **must** verify that the native public-release binding exposes no merge, approval, target-retargeting, protected-branch update, tag, or deployment effect and ends with an open PR result only.

## Details

The absence of merge is verified from the declared binding and mocked effect trace, not inferred from intent.
