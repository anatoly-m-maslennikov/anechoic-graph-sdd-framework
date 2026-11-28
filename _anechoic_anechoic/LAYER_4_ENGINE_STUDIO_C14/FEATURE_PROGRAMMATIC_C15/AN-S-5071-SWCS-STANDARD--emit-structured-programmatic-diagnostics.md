---
atom_family: SPEC
atom_id: AN-S-5071
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
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Emit structured PROGRAMMATIC diagnostics

## Semantics

Runtime diagnostics explain an operation's outcome to the Operator.
The process streams carry that evidence for requests and background work.
The `protocolStdoutClean` input means protocol stdout carries results only.

## Claim

### Formal Claim

```lean
namespace ProgrammaticDiagnostics

def conforms (structured sanitized protocolStdoutClean : Bool) : Bool :=
  structured && sanitized && protocolStdoutClean

end ProgrammaticDiagnostics
```

### Prose Claim

Use the shared diagnostic emitter. Apply AN-S-4741 to stream routing.
