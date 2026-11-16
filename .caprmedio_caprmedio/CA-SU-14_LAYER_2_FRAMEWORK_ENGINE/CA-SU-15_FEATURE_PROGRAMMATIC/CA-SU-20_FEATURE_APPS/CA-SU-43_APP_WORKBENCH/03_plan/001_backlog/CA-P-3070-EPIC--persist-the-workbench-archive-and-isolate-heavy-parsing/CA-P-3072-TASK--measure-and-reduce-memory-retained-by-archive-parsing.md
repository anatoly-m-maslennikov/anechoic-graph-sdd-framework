---
identity:
  atom_id: CA-P-3072
  ref_id: CA-P-3072
context:
  container:
    atom: CA-P-3070
  role: plan
  form: plan
  label: Task
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Indexing
  tier: 4
state:
  status: backlog
  version: 1
  updated_at: '2026-11-15T17:02:16.350801+00:00'
destination:
  file:
    name: CA-P-3072-TASK--measure-and-reduce-memory-retained-by-archive-parsing.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/03_plan/001_backlog/CA-P-3070-EPIC--persist-the-workbench-archive-and-isolate-heavy-parsing
---
## Summary

Measure and reduce memory retained by Archive parsing

## Objective

Profile Archive parsing and optional Python imports. Update and review RMEDO for any justified changes. Verify whether a short-lived worker reduces retained memory.

## Definition of Done

Compare RAM and query and watcher latency with the disk-backed baseline. Verify worker exit and memory reclamation if adopted. Record the decision and test evidence.
