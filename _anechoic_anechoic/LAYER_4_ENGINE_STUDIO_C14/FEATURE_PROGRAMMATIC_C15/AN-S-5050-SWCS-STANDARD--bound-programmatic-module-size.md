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
  version: 3
  updated_at: "2026-11-28T11:41:07+00:00"
---

## Summary

Bound PROGRAMMATIC Module size

## Semantics

The bound limits authored Python, JavaScript, and TypeScript Modules in
PROGRAMMATIC, including tests. Count each Svelte file as one Module.
Measure the source file as stored, including whitespace and line
endings. The limit is 6 KiB (6,144 bytes).

## Claim

### Formal Claim

```lean
namespace ProgrammaticModuleBounds

def conforms (moduleBytes : Nat) : Bool :=
  decide (moduleBytes ≤ 6144)

end ProgrammaticModuleBounds
```
