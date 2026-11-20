---
atom_family: SPEC
atom_id: AN-S-2737
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 36
  updated_at: 2026-11-08 20:06:37 +0400
---
## Summary

Record replacement transitions in the Journal

## Claim

### Prose Claim

The authoritative Journal event that archives a predecessor records its identity and one or more already Current successor Atom IDs.

IS_REPLACEMENT_FOR records the replacement Atom's predecessor links before and after adoption. A Draft link records proposed replacement. The Journal records the completed replacement or absorption transition.
