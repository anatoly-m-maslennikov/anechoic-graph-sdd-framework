---
atom_family: SPEC
atom_id: AN-S-3850
container:
  component: C20
tier: 0
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-11-09 19:30:15 +0400
---

## Summary

Coordinate Workflow Runs

## Claim

WORKFLOW_ORCHESTRATOR **must** own synchronous **and** asynchronous Workflow Run coordination, including interactive Step suspension, result submission, continuation, recovery, **and** next-Step selection from applicable methodology.

## Details

### Methodology-conforming execution boundary

WORKFLOW_ORCHESTRATOR **must** be the APPS Scope Unit that provides a conforming executor of the applicable methodology Workflow model under CA-R-1519 **and** CA-R-1520.

- for each accepted request, Tools remain realizations of individual methodology Actions under CA-R-1516.
- support Programmatic Actions **and** Agentic Steps. the Operator selects caller-coordinated execution **or** independent execution through an admitted worker adapter. independent execution launches isolated Agents **and** records their admitted results **without** requiring a live main session. caller-coordinated execution returns the Action prompt **and** invocation envelope through MCP. **only** admitted results permit progress; retain coordination state rather than requiring the session **to** remember the procedure.
- applicable Workflow definitions, input bindings, result conditions, **and** continuation rules determine execution. the application **must not** maintain a second independently authored Update-to-Replace rule **or** another Workflow-specific policy.
- the application's RMED specifies its execution behavior; Workflow definitions are governed inputs, **not** a requirement **to** use those Workflows **to** build the application.
- the application implements the methodology conformance requirements. its existence is **not** a backward Demand from FRAMEWORK_METHODOLOGY **to** FRAMEWORK_ENGINE.

The application is one immediate unordered APPS Scope Unit. Its declaration does not install a service **or** replace an existing specialized execution component.
