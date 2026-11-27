---
atom_family: TKT
atom_id: AN-T-4085
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T17:48:27.881294+00:00'
---
## Summary

Use one Backend REST Tool API for IWE Console and MCP

## Objective

Use the C91 Backend REST Tool API for Console and MCP Tool calls. Keep
Tool discovery, validation, dispatch, and Project admission in C91.

## Scope

Move Console Tool calls to the same-origin REST endpoint and remove
the Console-specific Tool invocation path. Preserve MCP discovery and
invocation, Console behavior, and the published Backend Tool contract.

## Done when

Console and MCP calls reach the same Backend Tool API. Focused tests
verify Project admission, Tool results and errors, and Console flows.
The affected formal contracts reflect the verified implementation.
