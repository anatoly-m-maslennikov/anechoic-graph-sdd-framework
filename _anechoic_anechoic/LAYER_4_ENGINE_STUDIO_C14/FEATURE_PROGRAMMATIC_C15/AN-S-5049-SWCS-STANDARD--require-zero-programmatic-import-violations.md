---
atom_family: SPEC
atom_id: AN-S-5049
concern:
  subject: IMPORTS
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: "active"
  version: 2
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Require zero PROGRAMMATIC import violations

## Semantics

Imports preserve Package ownership and Component code boundaries. This
Standard covers authored PROGRAMMATIC Python, JavaScript, TypeScript, and
Svelte imports, including tests.

## Claim

### Formal Claim

```lean
namespace ProgrammaticImports

def conforms
    (deniedImports undeclaredBypasses ownershipViolations : Nat) : Bool :=
  deniedImports + undeclaredBypasses + ownershipViolations == 0

end ProgrammaticImports
```

### Prose Claim

Use current source and Component Manifests for the Static import gate.
Allow exact declared entry bypasses. Report unresolved imports separately.
Fail the gate if the Component or its source cannot be checked.
