---
atom_family: SPEC
atom_id: AN-S-3425
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-10-04T05:54:48.186357+04:00'
---
## Summary

Reload MCP implementation without disconnecting

# Summary

Reload MCP implementation without disconnecting

## Scope

server-side hot reload for the Project-local MCP gateway.

## Claim

the MCP gateway **must** provide Operator-requested implementation reload while preserving the established transport connection **and** its fixed Project boundary.

## Details

- a successful reload makes one validated implementation generation available for new calls.
- a failed reload retains the previously serving generation **and** reports the failure.
- an in-flight call retains its admitted generation until it finishes; reload does **not** replay, cancel **or** migrate that call.
- reload **only** changes executable capability availability; it grants **no** new authority to mutate Atoms, start Workflows **or** launch workers.
- automatic file watching **and** operating-system startup hooks are outside this initial capability.

