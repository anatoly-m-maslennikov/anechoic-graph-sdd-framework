---
atom_family: TKT
atom_id: AN-T-4076
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-27T16:35:55.344004+00:00"
---
## Summary

Generate Backend OpenAPI from Tool descriptors

## Objective

Publish a build-generated OpenAPI contract for the shared beta Backend
Tool API. Use the live Tool descriptor source and keep MCP discovery
on the selected Backend's catalog.

## Scope

Cover the shared beta Tool catalog and invocation on /tools. Build on
the C75 HTTP Action pilot verified in AN-T-4000. Package the document
with the selected beta_next image.

## Done when

The packaged document describes the real HTTP envelopes and each Tool
input. OpenAPI validation, catalog parity, representative calls and
image packaging have focused evidence.
