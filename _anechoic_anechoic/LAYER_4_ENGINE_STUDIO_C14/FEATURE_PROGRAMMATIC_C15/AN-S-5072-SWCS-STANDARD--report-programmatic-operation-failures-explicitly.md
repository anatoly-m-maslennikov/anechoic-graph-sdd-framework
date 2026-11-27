---
atom_family: SPEC
atom_id: AN-S-5072
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
  CONTRIBUTES_TO:
  - AN-S-4741
state:
  status: active
  version: 1
  updated_at: '2026-11-27T11:11:44.727957+00:00'
---

## Summary

Report PROGRAMMATIC operation failures explicitly

## Semantics

The handling boundary records failures and lets the caller distinguish a
failed operation from success or an explicitly incomplete result.

## Claim

### Formal Claim

```lean
namespace ProgrammaticFailures

def conforms (failed hasCaller logged failureResult : Bool) : Bool :=
  !failed || (logged && (!hasCaller || failureResult))

end ProgrammaticFailures
```

### Prose Claim

Catch failures where the operation can handle them or report its outcome.
Emit a diagnostic at that boundary, including for background work.
Return a structured failure to HTTP and MCP callers, or a nonzero CLI exit.
Preserve the cause. Follow the Component contract for any partial result
or recovery and report the resulting outcome explicitly.
