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
  status: draft
  version: 1
  updated_at: '2026-11-27T09:44:56+00:00'
---

## Summary

Bound PROGRAMMATIC source size and line length

## Semantics

The bounds apply to PROGRAMMATIC source, including tests and executable
JavaScript and TypeScript family files. They limit each physical source line
and each Module and function, independent of whether a check is enabled.

## Claim

### Formal Claim

```lean
namespace ProgrammaticSourceBounds

def conforms (moduleLines functionLines lineCharacters : Nat) : Bool :=
  decide (moduleLines ≤ 300) && decide (functionLines ≤ 45) &&
    decide (lineCharacters ≤ 79)

end ProgrammaticSourceBounds
```

### Prose Claim

Limit each source Module to 300 nonblank lines and each function to 45
nonblank lines. Limit each physical line to 79 characters. Use the locked
frontend parser to measure web functions.
