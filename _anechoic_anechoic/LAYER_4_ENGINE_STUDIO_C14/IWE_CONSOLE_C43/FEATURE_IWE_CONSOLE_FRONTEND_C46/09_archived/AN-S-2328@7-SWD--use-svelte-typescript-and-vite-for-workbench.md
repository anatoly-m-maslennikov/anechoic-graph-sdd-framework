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
  version: 7
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Use Svelte, TypeScript and Vite for Workbench

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Use Svelte components and TypeScript for the Workbench frontend, and Vite for its production build. Serve static assets through the existing Python application. Node is required for building, not for serving the running application.

Keep presentation, formatting, page navigation and UI state in the frontend. Keep SQL execution, filtering, sorting, aggregation and stable result materialization in DuckDB. The browser requests bounded pages and does not load a complete large result to reproduce database operations.

Use the connector's `columns[].has_values` metadata, computed across the complete result, to hide fully empty columns in non-empty results. For this metadata only, NULL, empty strings, empty arrays and empty objects are empty; false and zero are values, and a nested object with keys is non-empty even when a nested value is null. For a zero-row result, the connector sets `has_values: true` for every returned column so all headers remain visible. This display choice does not change SQL values, row counts or column counts, and it stays identical across pages.

Reuse a small component palette from the start. Do not add a frontend router, state framework or separate web server for this query page.

When the frontend build is missing, keep the query API and MCP available. The Workbench page returns HTTP 503 with an explicit build-required error; do not build assets or start a frontend server automatically.

Use `/anechoic/workbench/<project_name>` for the selected Project. Read its declared Name from the existing gateway selection; do not infer it from a folder name or discover other repositories. A mismatched name returns HTTP 404. Shared-server requests retain their existing explicit Project-root selection and the URL Name must match it. Keep MCP at `/anechoic/mcp` and health at `/anechoic/health`.
