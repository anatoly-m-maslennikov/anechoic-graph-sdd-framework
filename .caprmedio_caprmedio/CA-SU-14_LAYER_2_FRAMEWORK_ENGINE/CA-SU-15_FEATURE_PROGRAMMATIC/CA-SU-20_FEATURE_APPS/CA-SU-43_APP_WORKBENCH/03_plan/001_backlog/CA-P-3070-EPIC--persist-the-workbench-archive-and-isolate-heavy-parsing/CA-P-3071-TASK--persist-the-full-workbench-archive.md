---
identity:
  atom_id: CA-P-3071
  ref_id: CA-P-3071
context:
  container:
    atom: CA-P-3070
  role: plan
  form: plan
  label: Task
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Storage <+ Temporary State
  tier: 4
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:02:13.170219+00:00'
destination:
  file:
    name: CA-P-3071-TASK--persist-the-full-workbench-archive.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/03_plan/001_backlog/CA-P-3070-EPIC--persist-the-workbench-archive-and-isolate-heavy-parsing
---
## Summary

Persist the full Workbench Archive

## Objective

Update and review RMEDO for the Project-local DuckDB path, full Archive indexing, and fast Atom allocation lookups. Implement and verify the reviewed spec.

## Definition of Done

Full Archive queries and exact revision lookups work after restart. Watcher changes update the Archive rows and allocation summaries. Record first-load peak RAM, idle RAM, and restart time.
