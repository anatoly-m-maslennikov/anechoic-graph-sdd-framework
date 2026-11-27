---
atom_family: SPEC
atom_id: AN-S-5046
concern:
  subject: Module
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content
  relation: is_contained_by
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: active
  version: 1
  updated_at: '2026-11-27T10:14:59.835668+00:00'
---

## Summary

Bound PROGRAMMATIC module and function size

## Semantics

The bounds limit authored Python, JavaScript, and TypeScript Modules in
PROGRAMMATIC, including tests. Count each Svelte file as one Module and
measure functions and methods in its script blocks.

## Claim

### Formal Claim

```lean
namespace ProgrammaticSourceBounds

def conforms (moduleLines functionLines : Nat) : Bool :=
  decide (moduleLines ≤ 300) && decide (functionLines ≤ 45)

end ProgrammaticSourceBounds
```

### Prose Claim

Limit each source Module to 300 nonblank lines and each function or method
to 45 nonblank lines. Use the locked frontend parser to measure web
functions.
