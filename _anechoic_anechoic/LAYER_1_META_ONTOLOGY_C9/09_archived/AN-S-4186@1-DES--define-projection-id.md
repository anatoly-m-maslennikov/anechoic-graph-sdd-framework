---
atom_family: SPEC
atom_id: AN-S-4186
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Projection ID

## Claim


Projection.ID is the stable identity of a Projection for its Projection Type, named source selection and source of truth. Rebuilding from changed source content or at another time keeps the ID while that identity tuple stays the same. Changing any tuple component requires a different ID under CA-R-1943.

### Formal claim

```text
Entity/Object/Continuant/Projection.ID[string]{1}
```

## Details

Source meaning: CA-R-1746, CA-R-1943. Scope-specific constraints remain in their governing Rs.
