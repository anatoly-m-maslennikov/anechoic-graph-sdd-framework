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
  version: 1
  updated_at: 2026-11-10 00:46:37 +0400
---

## Summary

Encode query result files as JSON matrix by default

## Claim scope

Shared Workbench query-result serialization.

## Claim

### Prose Claim

Use JSON matrix as the default result-file format. Store column names once in `columns` and ordered positional values in `rows`. Offer CSV and TOON as alternatives. Apply the same shared value encoding to every format.

Write results under the selected Project's `.anechoic_tmp/workbench/query_results`. Return metadata and the completed file path instead of embedding rows or full SQL in an ordinary MCP answer. Read from the existing materialized result; do not rerun SQL to export it. Keep browser grid pages available through explicit inline delivery.

Preserve column order, duplicate names, nulls, empty strings, Unicode, source newlines and Formal Claim text. Use the official TOON codec for the matrix value. For CSV use normal quoting, distinguishing unquoted null from quoted empty with matching typed readback. Do not stringify every cell or replace multiline claims with one line.

## Details

The 50-Atom comparison found CSV slightly smaller in tokens. JSON matrix is the Operator's selected default for its explicit value representation. This choice does not claim a token advantage or a model-comprehension result.
