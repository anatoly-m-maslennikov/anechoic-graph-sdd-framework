---
atom_family: TKT
atom_id: AN-T-3915
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T12:20:21.896016+00:00'
---
## Summary

Recall historical bugs from detached checkouts

## Work

Add an automated historical checkout-analysis stage to the golden corpus. Seek high recall across the 14 linked session candidates using actual detached checkouts of the old and fixed revisions. Bounded extra historical findings are acceptable. New scanner inputs are historical only; do not review current runtime.

Require exact historical source or a valid archived receipt for each claimed old and fixed state. Preserve provenance, commands, evidence, and the analysis outcome. Treat missing pairs and unsupported analysis as coverage gaps, not passes. Await measured results before claiming outcomes.

Known pending gaps are the incomplete historical failing state for Compose, and exact historical pair or analysis for the supervisor, original saved-query old-table graph, workflow guards, and namespace imports.

## Acceptance

The automated stage records coverage of the 14 linked candidates and any bounded additional findings. Each supported result has traceable old and fixed evidence from exact historical source or valid archived receipts. Missing pairs, unsupported cases, and unresolved recall gaps are explicit; no unsupported case is counted as a pass.
