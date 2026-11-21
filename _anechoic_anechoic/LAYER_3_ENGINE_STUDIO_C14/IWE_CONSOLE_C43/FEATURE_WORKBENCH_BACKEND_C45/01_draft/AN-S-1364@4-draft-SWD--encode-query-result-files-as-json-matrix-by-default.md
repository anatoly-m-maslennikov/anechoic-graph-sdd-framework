---
atom_family: SPEC
atom_id: AN-S-1364
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 4
  updated_at: '2026-11-13T22:31:17.173500+00:00'
---
## Summary

Encode query result files as JSON matrix by default

## Claim scope

Shared Workbench query-result serialization.

## Claim

### Prose Claim

JSON matrix is the default result-file format.

## Details

- `columns` stores names once. `rows` stores ordered positional values.
- CSV and TOON are alternatives. All formats use the shared value encoder.
- Export uses the existing materialized result without rerunning SQL.

### Value preservation

- Preserve order, duplicate names, nulls, empty strings, Unicode, source
  newlines, and Formal Claim text.
- Keep cell types and multiline Claims.
  - TOON uses the official codec.
  - CSV uses normal quoting. Unquoted empty represents null. Quoted empty
    represents an empty string.
