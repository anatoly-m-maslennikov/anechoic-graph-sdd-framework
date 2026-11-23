---
atom_family: TKT
atom_id: AN-T-1792
container:
  component: C14
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 14:24:58 +0400
---

## Summary

Deleted Atoms remain indexed after watcher idle

## Concern

After the C707 batch updated ten Current Atoms and removed two Current Method carriers and their owned Drafts, query_run still returned M417/M426 as Current although their source paths were absent and workbench_status reported syncing=false. A full Workbench reread removed both rows.

## Details

Reproduce the mixed update/delete batch and correct the incremental indexing path. Do not infer the internal cause from this observation. Preserve actual deletion semantics and add coverage through the existing watcher Evaluation E677. Source retirement was independently verified after the reread; this Problem remains Active until the code fix and acceptance are verified.
