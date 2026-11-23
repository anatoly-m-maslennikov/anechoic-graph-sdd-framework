---
atom_family: SPEC
atom_id: AN-S-3874
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-08-30 16:44:07 +0400
---
## Summary

Delegate one MCP call to its canonical Tool

# Delegate one MCP call to its canonical Tool

## Applicable when

Apply **when** MCP receives one validated request for an exposed Tool.

## Procedure

1. Select the canonical Tool executable from the current registry.
2. Forward the admitted request **without** reimplementing target resolution, project meaning, validation, mutation, recovery, **or** lifecycle semantics.
3. Transport the Tool result as a Tool result, retaining **every** failure **and** side-effect boundary.

## Outcome

MCP is a transport boundary **and** the canonical Tool remains the sole operation owner.

## Failure or stop

Stop **when** canonical selection, request validation, **or** delegated execution fails; do **not** substitute MCP behavior.
