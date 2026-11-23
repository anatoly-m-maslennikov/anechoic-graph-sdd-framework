---
atom_family: SPEC
atom_id: AN-S-2508
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 20
  updated_at: 2026-10-24 04:38:42 +0400
---
## Summary

Evaluate Scope Expressions

# Summary
Evaluate Scope Expressions

## Scope
evaluation of a Scope Expression.

## Claim
**to** evaluate one Scope Expression, the Resolver **must** perform **all** of:

1. resolve **every** exact Atom ID **or** other atomic identity **to** **`=1`** Governed Entity.
2. interpret **all** `<ENTITY_KIND>` as **every** Governed Entity of that kind within Atom Scope.
3. interpret **or** as set union.
4. interpret **and** as set intersection.
5. interpret **without** as left-side set exclusion.
6. interpret **where** as retention of **only** members whose field predicate evaluates **to** true according **to** `CA-M-122-CORE_META_MODEL-METHOD--evaluate-condition-expressions`.
7. evaluate the innermost parenthesized set function **before** its containing set function.
8. use another Scope function **only** **when** an active CCE Method gives that function **`=1`** set meaning.

## Details
