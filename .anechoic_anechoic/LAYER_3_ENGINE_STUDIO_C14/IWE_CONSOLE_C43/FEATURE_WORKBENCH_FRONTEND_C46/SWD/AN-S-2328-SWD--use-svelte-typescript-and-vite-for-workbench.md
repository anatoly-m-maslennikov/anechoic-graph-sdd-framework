---
identity:
  atom_id: AN-S-2328
context:
  container:
    component: C46
  tier: 4
  lens: SWD
state:
  status: active
  version: 9
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Use Svelte, TypeScript and Vite for Workbench

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Bind the frontend to the shared backend query, View and saved-resource contract. Preserve supplied request/result/cancellation/stale/error states; the frontend is neither backend authority nor effect owner.

Use Svelte components and TypeScript, built by Vite and served as static assets through the existing Python application. Node is build-only. Keep presentation, formatting, navigation and UI state in the browser; DuckDB owns SQL execution/filtering/sorting/aggregation and stable materialization. Request bounded pages rather than loading a complete large result.

Use complete-result `columns[].has_values` metadata to hide fully empty columns only in non-empty results: NULL, empty string/array/object are empty; false, zero and objects with keys are values. Zero-row results set every column true so headers remain visible. This display rule never changes values/counts and is identical across pages. Reuse a small component palette; add no router, state framework or second web server.
