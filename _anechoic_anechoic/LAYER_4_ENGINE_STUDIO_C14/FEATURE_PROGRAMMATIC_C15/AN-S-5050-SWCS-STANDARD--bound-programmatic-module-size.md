---
atom_family: SPEC
atom_id: AN-S-5050
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
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-5046
state:
  status: active
  version: 1
  updated_at: '2026-11-27T10:52:53.677257+00:00'
---

## Summary

Bound PROGRAMMATIC Module size

## Semantics

The bound limits authored Python, JavaScript, and TypeScript Modules in
PROGRAMMATIC, including tests. Count each Svelte file as one Module.

## Claim

### Formal Claim

```lean
namespace ProgrammaticModuleBounds

def conforms (moduleLines : Nat) : Bool :=
  decide (moduleLines ≤ 300)

end ProgrammaticModuleBounds
```

### Prose Claim

Limit each source Module to 300 nonblank lines. Include authored
PROGRAMMATIC tests and count each Svelte file as one Module.
