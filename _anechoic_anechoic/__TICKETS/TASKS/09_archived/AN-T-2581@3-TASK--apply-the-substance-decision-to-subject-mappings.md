---
atom_family: TKT
atom_id: AN-T-2581
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 06:04:15 +0400
---
## Summary

Apply the Substance decision to Subject mappings

# Summary

Apply the Substance decision to Subject mappings

## Objective

Align the exact legacy Claim field with the Operator-confirmed shared Substance field.

## Details

Estimated own work: 15 minutes. Required prerequisites: CA-P-2047 and persisted current ledger. Use the supplement contract. Recheck all 143 exact Atom/Claim occurrences across 142 source files and preserve source-specific evidence. Produce supplements/substance.review.json and a small ad-hoc support script with isolated tests. All 143 proposed values are Atom.Substance; 137 baseline candidates change and 6 were already aligned. Preserve every other occurrence, compound Claim path, source Content Role, quarantine finding and original byte. No live source write. Root independently accepts and commits the Task.

### Definition of Done

Not Done if assigned coverage or evidence is missing/stale, a meaning is guessed, unresolved work is hidden, Core or frozen evidence changes, an approval is inferred, tests fail, or own work exceeds 15 minutes without decomposition.

### Completion evidence

Created and independently accepted the exact 143-row bare Claim overlay from 142 pinned sources: all targets are Atom.Substance; 137 baseline candidates change and six were already aligned. The other 63 Claim-bearing rows remain excluded. Six isolated tests and live structural/evidence checks pass; a second write refuses overwrite. Independent meaning review confirms source roles and Operations body labels are preserved. The real receipt is `_projection/core-entity-review/stage2/task-2048.receipt.json`. Original Subjects, bodies and frozen evidence remain unchanged.
