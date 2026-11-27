---
atom_family: TKT
atom_id: AN-T-4080
container:
  component: C21
priority: 2
context:
  template: task
  label: Epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T17:14:26.444604+00:00'
---
## Summary

Evaluate a tools-only MCP adapter for C21

## Objective

Determine whether a smaller C21 adapter can reduce resident memory
and preserve the MCP behavior supported by ANECHOIC.

## Scope

Use the shared beta Backend from AN-T-4076. Keep Tool descriptors,
validation, dispatch, and Project admission in C91. Evaluate stdio
and stateless JSON over Streamable HTTP with supported clients.
Record which clients require sessions or SSE.

## Done when

Record a decision based on client compatibility and measured RAM.
If replacement proceeds, prove parity and savings before changing
the default. Treat removal of the SDK from the shared image as a
separate packaging result that requires an import audit.
