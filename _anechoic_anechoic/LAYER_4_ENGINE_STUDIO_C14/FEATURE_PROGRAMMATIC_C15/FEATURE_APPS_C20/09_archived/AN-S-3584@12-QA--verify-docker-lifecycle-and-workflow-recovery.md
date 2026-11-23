---
atom_family: SPEC
atom_id: AN-S-3584
container:
  component: C20
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-27 19:59:37 +0400
---
## Summary

verify Docker lifecycle **and** Workflow recovery

# Summary

verify Docker lifecycle **and** Workflow recovery

## Scope

the Docker runtime's mocked end-to-end **and** lifecycle tests.

## Claim

the Evaluation **must** verify that Docker lifecycle operations preserve authorized Workflow behavior **and** durable evidence **without** dispatch duplication.

## Details

- build the image **and** start a mock Agent plus real DBOS worker; verify current readiness rather than container existence alone.
- enqueue through MCP, disconnect the client, observe completion, confirmed Journal events **and** a full report.
- restart the worker **and** verify persistence of terminal results **without** another Agent call.
- interrupt an in-flight dispatch **and** verify recovery reports uncertainty rather than replaying it.
- verify stopped Docker routing fails visibly **and** leaves the native queue untouched.
- run mocks **without** live credentials **or** paid model calls; distinguish this evidence from a separately authorized real Agent pilot.
