---
atom_family: SPEC
atom_id: AN-S-5051
concern:
  subject: '(.Form in (function, method))'
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content/Module/Unit
  relation: is_narrower_than
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: archived
  version: 2
  updated_at: "2026-11-28T11:49:06+00:00"
---

## Summary

Bound PROGRAMMATIC Unit size

## Semantics

The bound limits function and method scope in authored Python, JavaScript,
and TypeScript Modules in PROGRAMMATIC, including tests. The `unitLines`
input counts nonblank lines.

## Claim

### Formal Claim

```lean
namespace ProgrammaticUnitBounds

def conforms (unitLines : Nat) : Bool :=
  decide (unitLines ≤ 45)

end ProgrammaticUnitBounds
```

### Prose Claim

Use the locked frontend parser to measure web functions, including
functions and methods in Svelte script blocks.
