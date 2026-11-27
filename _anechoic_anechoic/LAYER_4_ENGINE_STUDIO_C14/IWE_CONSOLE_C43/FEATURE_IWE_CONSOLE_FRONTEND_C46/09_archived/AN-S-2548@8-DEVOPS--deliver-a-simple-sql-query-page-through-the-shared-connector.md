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
  version: 8
  updated_at: 2026-11-04 21:06:25 +0400
---

## Summary

Deliver a simple SQL query page through the shared connector

## Claim scope

The Workbench frontend and its same-listener HTTP delivery.

## Claim

### Prose Claim

Build the Workbench frontend with Svelte, TypeScript and Vite. Serve its static production assets through the existing Python application at `/anechoic/workbench/<project_name>`; Node is a build dependency, not a second runtime server.

Provide a SQL editor, Run and Check controls, exact counts, query errors and ordinary result rows with Previous and Next page controls. Use shared components from a small component palette. Keep display formatting, page navigation and UI state in the frontend; the database executes SQL filtering, sorting and aggregation.

The frontend receives `columns[].has_values` computed over the complete materialized result. For this metadata only, NULL, empty strings, empty arrays and empty objects are empty; false and zero are values, and a nested object with keys is non-empty even when a nested value is null. For a non-empty result, hide only fully empty columns (`has_values: false`) while preserving row and column counts and all SQL values. For a zero-row result, the connector sets `has_values: true` for every returned column so all headers remain visible. The same column metadata and visibility decision applies to every page. Content column names remain the lowercase business-language names returned by SQL, including spaces in names such as `content.claim.prose claim`.

Use `/anechoic/workbench/<project_name>/run`, `/anechoic/workbench/<project_name>/page` and `/anechoic/workbench/<project_name>/check` for the shared connector. Fetch only the requested result page. Preserve positional values and duplicate column names. Show loading and error states and accessible labels for controls. Do not add custom TABLE, DOC or TREE modes, a second query evaluator or a separate web service.

When the frontend build is missing, keep the query API and MCP available. The Workbench page returns HTTP 503 with an explicit build-required error; do not build assets or start a frontend server automatically.

For the current Project, the page is `/anechoic/workbench/anechoic`. Keep shared static assets under `/anechoic/workbench/assets`. The frontend sends Run, Page and Check requests under its current Project page path. The URL's Project name must match the existing selected Project; a mismatched name returns HTTP 404.

Keep the result table in a bounded scrolling region, with visible column headers and separately scrollable long cell values. Preserve every row and value; scrolling changes presentation, not the query result.
