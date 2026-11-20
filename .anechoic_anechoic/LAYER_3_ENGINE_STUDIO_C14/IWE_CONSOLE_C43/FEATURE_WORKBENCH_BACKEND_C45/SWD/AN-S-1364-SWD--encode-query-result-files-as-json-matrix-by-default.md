---
identity:
  atom_id: AN-S-1364
context:
  container:
    component: C45
  tier: 4
  lens: SWD
state:
  status: active
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Encode query result files as JSON matrix by default

## Claim scope

Shared Workbench query-result serialization.

## Claim

### Prose Claim

Use JSON matrix as the default result-file format: `columns` stores names once and `rows` stores ordered positional values. CSV and TOON are alternatives and all formats use the shared value encoder.

Write under the selected Project's `.anechoic_tmp/workbench/query_results`. Return completed file metadata/path, not rows or full SQL, in ordinary MCP responses; export from the existing materialized result without rerunning SQL. Explicit inline delivery keeps browser grid pages available. Preserve order, duplicate names, nulls, empty strings, Unicode, source newlines and Formal Claim text. Use the official TOON codec; CSV normal quoting must distinguish unquoted null from quoted empty. Do not stringify every cell or flatten multiline claims.
