---
atom_family: SPEC
atom_id: AN-S-1364
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T20:54:14.451893+00:00'
---
## Summary

Encode query result files as JSON matrix by default

## Claim scope

Shared Workbench query-result serialization.

## Claim

### Prose Claim

Use JSON matrix as the default result-file format. `columns` stores names once and `rows` stores ordered positional values. CSV and TOON are alternatives. All formats use the shared value encoder.

Export the existing materialized result without rerunning SQL.

Preserve order, duplicate names, nulls, empty strings, Unicode, source newlines and Formal Claim text. Use the official TOON codec. CSV normal quoting must distinguish unquoted null from quoted empty. Do not stringify every cell or flatten multiline claims.
