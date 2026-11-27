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
  status: active
  version: 2
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

Emit structured PROGRAMMATIC diagnostics

## Semantics

Runtime diagnostics explain an operation's outcome to the Operator.
The process streams carry that evidence for requests and background work.

## Claim

### Formal Claim

```lean
namespace ProgrammaticDiagnostics

def conforms (structured onStderr sanitized protocolStdoutClean : Bool) : Bool :=
  structured && onStderr && sanitized && protocolStdoutClean

end ProgrammaticDiagnostics
```

### Prose Claim

Use the shared diagnostic emitter under AN-S-4741. Reserve protocol
stdout for results.
