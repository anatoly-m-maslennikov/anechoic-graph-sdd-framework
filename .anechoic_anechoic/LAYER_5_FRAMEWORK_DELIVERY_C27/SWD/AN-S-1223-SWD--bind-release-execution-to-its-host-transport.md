---
identity:
  atom_id: AN-S-1223
context:
  container:
    component: C27
  tier: 4
  lens: SWD
state:
  status: active
  version: 19
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

bind Release execution to its host transport

## Claim

### Prose Claim

the direct host release entrypoint **must** bind **every** Local or Public Release invocation **to** its validated operation, Project root and Run ID before invoking the corresponding release implementation.

## Details

### Scope

direct Local and Public Release invocation through the host entrypoint.

- resolve the supplied Project root strictly and refuse a symlink, non-directory or filesystem root. Validate the operation and Run ID before the release implementation is called.
- bind `local` to `run_local_release` and `public` to `run_public_release`; only Public Release accepts the separately validated optional content draft.
- pass the resolved Project root and Run ID directly to that implementation. Its own project-relative runtime and temporary paths remain within that Project; the MCP process environment is not used to select or carry release execution.
- attempt Journal start and terminal observations around the invocation, but return the independently observed release outcome even when either observation fails.
- do not create or adopt a Queue, worker, private readiness carrier, DBOS Workflow or recovery transport. A failed invocation stops with its explicit result.
