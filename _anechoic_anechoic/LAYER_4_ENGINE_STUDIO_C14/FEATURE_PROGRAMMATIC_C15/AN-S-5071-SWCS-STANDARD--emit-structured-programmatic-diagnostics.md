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
  version: 1
  updated_at: '2026-11-27T11:11:44.727957+00:00'
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

Use the shared diagnostic emitter and the Studio logging levels. Emit bounded,
sanitized records to stderr with UTC time, component, event code, operation,
outcome, and an existing correlation ID when available.
Keep protocol stdout for results. Keep diagnostics free of secrets and raw
request data. Emit each exception trace once at its handling boundary.
