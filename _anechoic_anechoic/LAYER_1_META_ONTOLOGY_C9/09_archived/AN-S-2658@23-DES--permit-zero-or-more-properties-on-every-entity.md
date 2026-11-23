---
atom_family: SPEC
atom_id: AN-S-2658
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-30 17:41:00 +0400
---
## Summary

Permit Zero or More Properties on Every Entity

## Claim scope

Property occurrences borne by every Entity.

## Claim

**every** Entity **may** bear **`>=0`** Property occurrences.

### Formal claim

```text
Entity {0+}((HAS_PROPERTY)){1} Property
```
