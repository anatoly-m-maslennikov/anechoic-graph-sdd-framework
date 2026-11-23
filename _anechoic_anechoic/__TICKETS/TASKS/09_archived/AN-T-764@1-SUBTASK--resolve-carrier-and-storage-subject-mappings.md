---
atom_family: TKT
atom_id: AN-T-764
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 1
  updated_at: 2026-10-11 03:20:22 +0400
---
## Summary

Resolve carrier and storage Subject mappings

# Summary

Resolve carrier and storage Subject mappings

## Objective

Determine candidate targets for the 114 assigned unresolved Subject occurrences from current evidence.

## Details

Estimated own work: 15 minutes. Read the supplement contract and the exact carriers ownership entry in current-subjects.research-ownership.json. Scope: 114 occurrences, 90 source files, 63 distinct old values. Pin and read the applicable definitions and every source span supporting a proposed mapping. Resolve repetitive fields using common confirmed rules plus source-specific meaning, not display-string availability. Preserve all qualifiers and source identities. Output .anechoic_anechoic/_projection/core-entity-review/stage2/supplements/carriers.review.json. Full assigned coverage includes explicit unresolved rows; unresolved research must remain tracked. If all mapping work cannot fit 15 minutes, return verified partial results and exact remainder for decomposition; do not mark this Task Done or overrun. No Core, Plan, frozen report, Git, MCP/FPF or runtime writes.

### Definition of Done

Not Done if assigned coverage or evidence is missing/stale, a meaning is guessed, unresolved work is hidden, Core or frozen evidence changes, an approval is inferred, tests fail, or own work exceeds 15 minutes without decomposition.
