---
atom_family: SPEC
atom_id: AN-S-4621
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Diagnose failures in shared implementation context

# Summary

Diagnose failures in shared implementation context

## Operation

Implementation Failure Diagnosis Step **means** the Workflow node invoking **=1** Action, CA-O-089, **in** Integrated context under CA-R-1527.

- bind inputs from the same retained participating-session context, selected P/Plan, current candidate **and** phase, failure evidence from CA-O-094 or confirmed review findings from CA-O-230, test definitions, direct full `methods` rows **and** R/E/D, **and** applicable confidence **and** permission gates. An optional legacy `method_projection` may accompany those rows but is not required.
- use the host's native session/subagent, file, **and** command capabilities; this binding has no MCP prerequisite. missing required context **or** capability returns a blocked invocation, **not** silent execution **in** another context.
- retain exact Action/Step Revisions, source bindings, actual effects, **and** returned results. pass the Action's result **to** the Workflow **without** independently copying its behavior.

Retain the participating session and complete source-bound work/evidence across these Integrated invocations. A replacement requires a complete retained handoff and fresh admission; conversational memory alone is not evidence.

- retain shared request/Plan, current source-bound R/M/E/D, exact candidate and actual prior results, findings, and remaining retry/resource state. This explicit Integrated binding does not alter the context of standalone review Steps.

## Details
