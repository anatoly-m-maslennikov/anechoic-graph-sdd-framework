---
atom_family: TKT
atom_id: AN-T-4037
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T01:30:47.385326+00:00"
---
## Summary

Compile Project Specs from ingested rows

## Acceptance

Feed C51 Formal Model, C93 Project Structure, and C94 Formal Specification from the C95 source boundary. Keep authored Markdown reads with ingestion. Preserve exact source pin checks.

## Evidence

The managed compiler checks Model rows against the admitted Spec snapshot
and uses that same snapshot for Structure. The formal reader admits
exact pins from C95 rows. The managed startup and snapshot pin checks
passed in `an-t-3476-asset-and-snapshot.xml`.
