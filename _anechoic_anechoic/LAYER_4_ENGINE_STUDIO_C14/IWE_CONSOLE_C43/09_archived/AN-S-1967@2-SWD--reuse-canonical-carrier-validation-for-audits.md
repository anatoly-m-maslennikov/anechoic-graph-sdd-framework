---
atom_family: SPEC
atom_id: AN-S-1967
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: '2026-11-12T01:42:24.596360+00:00'
---

## Summary

Reuse canonical carrier validation for audits

## Claim

### Prose Claim

Reuse the existing source reader, locator and canonical carrier validation for the five Workbench audit tables. Audit the same selected Current, Draft and Backlog scan and any loaded Archive sources. Compare duplicate ID and Version pairs only for Current and Archived rows.

Measure audit elapsed time separately from source capture, relation materialization and DuckDB writes. Coalesce audit work for committed source changes and perform it outside the lifecycle response path. Apply the diagnostic changes for the latest affected paths so an older result cannot replace diagnostics for a newer source state. Keep the audit tables query-visible and leave source files unchanged.
