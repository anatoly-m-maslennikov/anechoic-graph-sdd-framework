---
atom_family: SPEC
atom_id: AN-S-2328
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 18:09:13 +0400
---

## Summary

Use Svelte, TypeScript and Vite for Workbench

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Use Svelte components and TypeScript for the Workbench frontend, and Vite for its production build. Serve static assets through the existing Python application. Node is required for building, not for serving the running application.

Keep presentation, formatting, page navigation and UI state in the frontend. Keep SQL execution, filtering, sorting, aggregation and stable result materialization in DuckDB. The browser requests bounded pages and does not load a complete large result to reproduce database operations.

Reuse a small component palette from the start. Do not add a frontend router, state framework or separate web server for this query page.

When the frontend build is missing, keep the query API and MCP available. The Workbench page returns HTTP 503 with an explicit build-required error; do not build assets or start a frontend server automatically.
