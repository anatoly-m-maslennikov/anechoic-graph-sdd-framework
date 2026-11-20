---
identity:
  atom_id: AN-S-2787
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 20
  updated_at: '2026-11-11T18:31:44+04:00'
---
## Summary

Use Subject Path Separators for Broader-to-Narrower and Bearer-to-Dependent

## Claim

### Prose Claim

- Use `X/Y` for a narrower declared kind, `X//Name` for a named instance, and `X.p` for a dependent Property.
- Use `X/(.p := V)` to select the qualified kind. Apply X’s inherited constraints to the selected kind. Existing Subjects using `:` retain their admitted interpretation.
- Keep the complete qualification of the Subject. The Subject expression can identify an existing target or one introduced by its defining Atom.
- Use the current Subject notation in CA-R-1321 for composition, classification, named Relations, and endpoint counts.
