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
  status: draft
  version: 2
  updated_at: '2026-11-27T11:20:14+00:00'
---

## Summary

Report PROGRAMMATIC operation failures explicitly

## Semantics

Apply this Standard by default to Programmatic public operations and
background work. A failed operation is observable through the outcome
channel declared by its Contract.

## Claim

### Formal Claim

```lean
namespace ProgrammaticFailures

inductive Channel where
  | background
  | response
  | exitCode

def conforms (channel : Channel)
    (failed diagnosticReported responseFailure nonzeroExit : Bool) : Bool :=
  !failed || (diagnosticReported && match channel with
    | .background => true
    | .response => responseFailure
    | .exitCode => nonzeroExit)

example : conforms .response true true true false = true := by rfl
example : conforms .response true true false true = false := by rfl
example : conforms .exitCode true true false true = true := by rfl
example : conforms .exitCode true true true false = false := by rfl
example : conforms .background true false false false = false := by rfl

end ProgrammaticFailures
```

### Prose Claim

Use the shared operation failure boundary where it applies. Report
a stable error code, a safe message, and the known target or source
and field. Preserve the cause and report a diagnostic under AN-S-5071.
If the diagnostic sink fails, report the sink failure through an
available channel and retain the primary outcome.

For a response protocol, return the failure result declared by the
Component Contract. A valid response may carry a denial or failure
with a successful transport status. Use a nonzero exit for a failed
CLI operation when the Contract reports failure by process exit code.

The Solution names its shared failure type or handler. It defines
which failures stop the operation, which effects remain, and what
the caller receives. Apply AN-S-1255@14 to partial and uncertain effects.
Reuse the shared failure handling in AN-S-1252@17.
