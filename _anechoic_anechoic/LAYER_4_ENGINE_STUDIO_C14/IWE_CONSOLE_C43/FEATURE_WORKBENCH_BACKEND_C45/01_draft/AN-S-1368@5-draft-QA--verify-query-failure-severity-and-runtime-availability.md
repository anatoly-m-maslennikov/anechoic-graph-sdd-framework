---
atom_family: SPEC
atom_id: AN-S-1368
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T23:56:14.732491+00:00'
---
## Summary

Verify query-failure severity and runtime availability.

## Claim

### Prose Claim

Verify that Workbench reports query and runtime failures at the right severity
and keeps a healthy owner usable after a rejected request.

## Details

### Invalid SQL or query arguments

- Return a useful request error.
- Log `query_error` at WARNING.
- Return `outcome: failed`.
- Verify that a valid native MCP/HTTP request succeeds after an invalid one.

### Runtime failures

When Workbench is unavailable or the runtime fails unexpectedly:

- Log at ERROR.
- Return `outcome: blocked`.
- Keep the restart/runtime boundary.
