---
atom_family: SPEC
atom_id: AN-S-1223
container:
  component: C27
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 20
  updated_at: '2026-11-21T21:49:04.407565+00:00'
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
- execute without importing or calling ANECHOIC runtime Components or Journal.
- do not create or adopt a Queue, worker, private readiness carrier, DBOS Workflow or recovery transport. A failed invocation stops with its explicit result.
