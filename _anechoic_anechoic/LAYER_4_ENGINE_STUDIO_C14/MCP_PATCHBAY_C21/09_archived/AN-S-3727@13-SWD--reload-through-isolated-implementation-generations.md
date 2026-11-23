---
atom_family: SPEC
atom_id: AN-S-3727
container:
  component: C21
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-11-07 04:28:07 +0400
---
## Summary

Reload through isolated implementation generations

# Summary

Reload through isolated implementation generations

## Scope

server-side hot reload for the Project-local MCP gateway.

## Claim

MCP hot reload is optional and disabled by default. Default startup serves tool implementations in the MCP process, without an implementation child. Apply code changes with a normal server/container restart. Only explicit opt-in enables isolated implementation generations and their existing validated switch behavior.

## Details

The following generation rules apply only when hot reload is explicitly enabled. When disabled, there is no implementation generation to replace or drain; preserve the same Project boundary, transport protections and callable tools. Do not advertise a working reload action in disabled mode.

1. keep the stdio gateway, protocol session, reload control **and** fixed Project binding stable.
2. load candidate code **and** dependencies in a separate local implementation process, rather than mutating live imported modules with importlib.reload.
3. initialize the candidate without starting Workflows, workers **or** source mutations; obtain its complete Tool contracts **and** validate names, schemas **and** the fixed Project binding.
4. switch new dispatch to the candidate **only** after validation succeeds; preserve the old generation for admitted calls.
5. drain retired generations **after** their admitted calls finish; expose a bounded drain failure rather than silently terminating uncertain effects.
6. when preparation fails, discard the candidate **and** keep the current generation. when a published generation later fails, report affected calls honestly; never replay a mutating call automatically.
7. serialize reload requests **and** suppress duplicate request IDs; an unchanged implementation frontier is a no-op.

