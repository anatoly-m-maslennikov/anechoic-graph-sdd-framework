---
atom_family: TKT
atom_id: AN-T-4002
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:36:16.810963+00:00"
---
## Summary

Check compatibility of published HTTP Contracts

## Acceptance

Compare an approved OpenAPI baseline and candidate with oasdiff. Prove the gate detects a breaking fixture and accepts a compatible fixture. Add Pact provider verification where an independently evolving consumer has a concrete interaction and provider state. Record when those prerequisites are absent.

## Verification

The approved C45 `query_run` baseline is the OpenAPI export of
`AN-S-3059@60-draft`. The Spec Engine compatibility test pins that
snapshot and uses oasdiff 1.41.0. It accepts the current export and a
documentation change. It rejects removal of the POST operation.

MCP Patchbay and Workbench's Project Tool Session call the private C45
socket. Both ship with the provider in the same Studio image. No
independently evolving caller of this endpoint was identified. The
private-socket process test covers the native caller.
