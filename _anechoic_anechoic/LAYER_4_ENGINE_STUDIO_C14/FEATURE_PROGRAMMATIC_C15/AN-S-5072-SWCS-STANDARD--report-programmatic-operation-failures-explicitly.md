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
  status: "active"
  version: 3
  updated_at: "2026-11-27T20:43:50.902996+00:00"
---

## Summary

Report PROGRAMMATIC operation failures explicitly

## Semantics

Apply this Standard by default to Programmatic public operations and
background work. A failed operation is observable through the outcome
channel declared by its Contract. A valid response may carry an
operation failure with a successful transport status.

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

Use the shared operation failure boundary where it applies. Preserve the
cause. Report a stable error code, a safe message, and the known target
or source and field. Apply AN-S-5071 to diagnostic records. If the sink
fails, report that failure through an available channel and retain the
primary outcome.

Use the failure result shape declared by the Component Contract. The
Solution names its shared failure type or handler and defines where
execution stops, which effects remain, and what the caller receives.
Apply AN-S-1255@14 to partial and uncertain effects and AN-S-1252@17
to shared failure handling.
