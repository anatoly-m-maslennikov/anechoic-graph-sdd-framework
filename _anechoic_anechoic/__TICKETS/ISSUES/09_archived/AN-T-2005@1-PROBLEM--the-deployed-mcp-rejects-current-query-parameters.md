---
atom_family: TKT
atom_id: AN-T-2005
container:
  component: C43
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 17:43:47 +0400
---

## Summary

The deployed MCP rejects current query parameters.

## Concern

The deployed MCP schema exposes only `sql`, `page_size`, and
`cursor_position` for the Workbench query operation, so it rejects
`preview: 0` and `save: false`. The current source schema includes these
options, and the SDK regression passes the exact `preview: 0` and `save: false`
request, but no deployed verification has been completed. Local source success
therefore does not establish deployed adoption.

## Resolution

This Problem remains open. The source correction and local regression evidence
are recorded, but deployment must still be verified to advertise and accept
optional `preview` and `save`, including `preview: 0` and `save: false`. Do not
mark the deployed boundary resolved until that endpoint-level check succeeds.
