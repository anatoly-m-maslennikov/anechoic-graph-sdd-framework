---
atom_family: SPEC
atom_id: AN-S-3588
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-11-07 04:28:07 +0400
---
## Summary

reload MCP implementation **without** disconnecting

## Claim scope

server-side hot reload for the Project-local MCP gateway.

automatic file watching **and** operating-system startup hooks are outside this initial capability.

## Claim

### Prose Claim

When optional hot reload is explicitly enabled, the MCP gateway **must** provide Operator-requested implementation reload while preserving the established transport connection **and** its fixed Project boundary.

Hot reload is disabled by default; normal restart applies code changes in that mode. When enabled, the reload capability has these required outcomes:

- a successful reload makes **`=1`** validated implementation generation available for new calls.
- a failed reload retains the previously serving generation **and** reports the failure.
- an in-flight call retains its admitted generation **until** it finishes; reload does **not** replay, cancel **or** migrate that call.

## Details

- reload **only** changes executable capability availability; it grants **no** new authority **to** mutate Atoms, start Workflows **or** launch workers.

