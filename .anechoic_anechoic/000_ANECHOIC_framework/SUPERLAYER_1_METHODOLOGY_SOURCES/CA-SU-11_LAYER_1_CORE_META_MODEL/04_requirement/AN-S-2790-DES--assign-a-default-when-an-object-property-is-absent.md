---
identity:
  atom_id: AN-S-2790
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Assign a default when an Object Property is absent

## Claim

### Prose Claim



- A fallback chain returns the first available value from left to right. An omitted value, null, or an empty string is empty. Zero and false are values.
- A reached nonempty value must satisfy the applicable Format and cardinality. Invalid values are errors.
- Evaluate each fallback only when needed. An exhausted chain, an evaluated cycle, or multiple applicable chains is an error.
- A fallback expression can read a literal, a Property on the same bearer, an explicitly bound Property, or a contextual lookup. An explicit foreign-bearer read requires one resolved target.
- The result is an effective value. The Property and its Carrier retain their authored values.

The Python Property Declaration specifies the fallback. For example,
`Atom.Header.Context.Label` uses `Form` when `Label` is empty.
