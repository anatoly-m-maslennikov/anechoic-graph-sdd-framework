---
atom_family: SPEC
atom_id: AN-S-2548
container:
  component: C46
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 6
  updated_at: 2026-11-04 18:09:13 +0400
---

## Summary

Deliver a simple SQL query page through the shared connector

## Claim scope

The Workbench frontend and its same-listener HTTP delivery.

## Claim

### Prose Claim

Build the Workbench frontend with Svelte, TypeScript and Vite. Serve its static production assets through the existing Python application at `/anechoic/workbench`; Node is a build dependency, not a second runtime server.

Provide a SQL editor, Run and Check controls, exact counts, query errors and ordinary result rows with Previous and Next page controls. Use shared components from a small component palette. Keep display formatting, page navigation and UI state in the frontend; the database executes SQL filtering, sorting and aggregation.

Use `/anechoic/workbench/run`, `/anechoic/workbench/page` and `/anechoic/workbench/check` for the shared connector. Fetch only the requested result page. Preserve positional values and duplicate column names. Show loading and error states and accessible labels for controls. Do not add custom TABLE, DOC or TREE modes, a second query evaluator or a separate web service.

When the frontend build is missing, keep the query API and MCP available. The Workbench page returns HTTP 503 with an explicit build-required error; do not build assets or start a frontend server automatically.
