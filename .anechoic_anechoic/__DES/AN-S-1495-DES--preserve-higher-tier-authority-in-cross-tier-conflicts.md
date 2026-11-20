---
atom_family: SPEC
atom_id: AN-S-1495
structure:
  container:
    component: C00
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Preserve higher-tier authority in cross-tier conflicts

## Claim

### Prose Claim


a conflict between active Requirements at different global tiers **must** preserve the lower-numbered claim **and** reconcile the higher-numbered claim **without** changing the lower-numbered meaning.
