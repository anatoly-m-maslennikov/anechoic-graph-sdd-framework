---
atom_family: SPEC
atom_id: AN-S-1940
container:
  component: C43
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Rebuild Workbench derived state from source

## Claim

Workbench can perform a full reread of its governed source files. A full reread drops and recreates the dedicated DuckDB database, its WAL and temporary files, all Workbench schema, graph and query-result tables, and then reads the source again. It preserves source files, saved queries and Worksheets, and does not delete source Journal records. It returns success only after the new Workbench state is ready. An invalid Scope Unit Declaration or startup failure returns an explicit failure and leaves Workbench unavailable until another explicit operation. The operation does not retry automatically.

## Details

Full reread may discard ephemeral query-result IDs because the derived result tables are recreated. It does not delete source Atoms, Scope Unit Declarations, saved items or Journal records.
