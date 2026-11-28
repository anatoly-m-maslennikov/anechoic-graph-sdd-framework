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
  status: active
  version: 4
  updated_at: "2026-11-28T12:13:48+00:00"
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

def conforms (unitLines nestingDepth : Nat) : Bool :=
  decide (unitLines ≤ 45 ∧ nestingDepth ≤ 4)

end ProgrammaticUnitBounds
```

### Prose Claim

#### Control-flow nesting

Measure control-flow depth in each function and method's syntax tree.
Count conditional, loop, try, and match or switch statements. Count each
if/elif/else or if/else-if/else chain as one level. Measure nested
functions and methods independently. Use the locked frontend parser
for web functions, including Svelte scripts.
