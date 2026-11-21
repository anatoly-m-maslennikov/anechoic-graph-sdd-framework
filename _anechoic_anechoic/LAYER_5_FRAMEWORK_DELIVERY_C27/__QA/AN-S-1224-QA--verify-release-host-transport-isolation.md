---
atom_family: SPEC
atom_id: AN-S-1224
container:
  component: C27
tier: 6
context:
  lens: QA
state:
  status: active
  version: 19
  updated_at: '2026-11-21T21:49:04.407565+00:00'
---

## Summary

verify Release host transport isolation

## Claim

### Prose Claim

the Evaluation **must** verify that the direct host release entrypoint validates each Local or Public invocation and keeps its Project-local release effects separate from the Docker/MCP runtime.

## Details

### Scope

the direct host invocation boundary for Local and Public Release.

- accept valid Local and Public operation arguments only when their Project root and Run ID pass the entrypoint validation, and verify the matching release implementation receives those same values.
- reject an invalid root, symlink root or Run ID before release dispatch.
- verify the direct host implementation places Local Release runtime/report artifacts below `.anechoic_runtime/simple_local_release/` and transient artifacts below `.anechoic_tmp/simple_local_release/`, without making either authoring authority.
- verify the entrypoint does not create or call a Workflow Orchestrator Queue, worker, private IPC health exchange or DBOS Workflow.
- verify release execution imports no ANECHOIC runtime Components and calls no Journal.
- verify Local Release invokes C19 Test Suite for unit, end-to-end and canary checks, and Public Release prepares drafts without running a suite.
