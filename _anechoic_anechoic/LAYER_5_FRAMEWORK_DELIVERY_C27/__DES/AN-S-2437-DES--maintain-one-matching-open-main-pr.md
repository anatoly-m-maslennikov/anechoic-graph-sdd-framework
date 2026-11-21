---
atom_family: SPEC
atom_id: AN-S-2437
structure:
  container:
    component: C27
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 13
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Maintain one matching open `main` PR

## Scope

one public release Pull Request boundary.

## Claim

### Prose Claim

**the Operator** **must** discover, create, or update exactly one actual open PR from the selected `amm/dev` head to `main` on the selected personal remote.

## Details

Zero matches permits create after the actual initial push. More than one match, a changed existing identity, or an unsafe/nonmatching URL blocks the Workflow.
