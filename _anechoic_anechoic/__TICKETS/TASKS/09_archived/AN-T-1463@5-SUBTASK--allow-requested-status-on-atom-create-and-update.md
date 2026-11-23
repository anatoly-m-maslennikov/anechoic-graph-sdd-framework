---
atom_family: TKT
atom_id: AN-T-1463
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 06:12:26 +0400
---
## Summary

Allow requested Status on Atom create and update

# Summary

Allow requested Status on Atom create and update

## Objective

Singular and existing bulk interfaces support all admitted Status values and explicit transitions, including Draft-to-Active and true no-op. Missing, empty, incomplete or unavailable Journal cannot deny or invalidate an otherwise valid mutation; append failure is reported separately and never causes effect replay.

## Details

### Observed completion — 2026-10-16

The requested-Status receiving changes and independent Journal recording paths were implemented and reviewed through CA-P-2397/2398. Four connected MCP journeys and the 24-test Linux bundle passed in observed initial image runs; frozen-image verification remains under CA-P-2389/2390. This bounded implementation closure neither closes the native concurrency work nor claims installed runtime activation.

Support create directly in any Status admitted by the Content Role, and explicit update to any such target Status. Remove MCP-only Active/Draft restrictions, mandatory staged transition paths and Journal-read/completeness/receipt admission prerequisites from affected mutations. Preserve ordinary schema, identity/collision, explicit target/delta, current-source and permission safeguards. Do not introduce a transition matrix.

Estimated own work: at most 15 minutes; split further before execution if needed. After completion, review/update the next dependent task. A blocked leaf is postponed with a truthful Problem/Question Concern as appropriate; independent ready work continues.

## Definition of Done

Singular and existing bulk interfaces support all admitted Status values and explicit transitions, including Draft-to-Active and true no-op. Missing, empty, incomplete or unavailable Journal cannot deny or invalidate an otherwise valid mutation; append failure is reported separately and never causes effect replay.

### Bounded execution split

The mapped work exceeds one leaf. Coordinate the following exclusive scopes, at most 15 minutes each; review dependencies before integration:

- [CA-P-2397](03-CA-P-2388@5-TASK--allow-requested-status-on-atom-create-and-update/done/01-CA-P-2397-TASK--remove-wrapper-journal-admission-gates.md)
- [CA-P-2398](03-CA-P-2388@5-TASK--allow-requested-status-on-atom-create-and-update/done/02-CA-P-2398-TASK--remove-subject-batch-recording-gates.md)
