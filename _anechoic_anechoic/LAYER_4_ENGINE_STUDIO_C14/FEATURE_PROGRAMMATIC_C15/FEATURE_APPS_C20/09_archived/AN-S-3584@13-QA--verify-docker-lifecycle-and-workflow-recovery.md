---
atom_family: SPEC
atom_id: AN-S-3584
container:
  component: C20
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

verify Docker lifecycle **and** Workflow recovery

## Claim

### Prose Claim

This retained contract applies only when AI-Agent execution is separately admitted. It does not enable that execution or claim that its runtime implementation is present.

the Evaluation **must** verify that Docker lifecycle operations preserve authorized Workflow behavior **and** durable evidence **without** dispatch duplication.

## Details

### Scope

the Docker runtime's mocked end-to-end **and** lifecycle tests.

- build the image **and** start a mock Agent plus real DBOS worker; verify current readiness rather than container existence alone.
- enqueue through MCP, disconnect the client, observe completion, confirmed Journal events **and** a full report.
- restart the worker **and** verify persistence of terminal results **without** another Agent call.
- interrupt an in-flight dispatch **and** verify recovery reports uncertainty rather than replaying it.
- verify stopped Docker routing fails visibly **and** leaves the native queue untouched.
- run mocks **without** live credentials **or** paid model calls; distinguish this evidence from a separately authorized real Agent pilot.
