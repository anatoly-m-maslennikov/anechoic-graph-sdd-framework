---
atom_family: TKT
atom_id: AN-T-3485
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T04:00:27.176626+00:00"
---
## Summary

Generate and compare Studio implementation Lean

## Work

Use Spec Engine and its child Components for the current implementation
verification. Generate Lean evidence from their actual code independently
of the authored Manifest and Solution. Compare both in Lean with exact
source pins, and report unresolved obligations.

Use one additional Component example when it exposes a gap in the eDSL
or verifier. Edit a Spec Engine carrier when it resolves a confirmed
mismatch or proves a fix.

## Findings

Fourteen Lean blocks and 21 workflow declarations compile. A Lean 4.19 compatibility shim works in scratch. Full conformance remains unsupported. Retain unresolved cases and do not close this comparison.

The Lean 4.31.0 baseline checked C75 and all eight children. The full
Spec Engine suite passed 244 tests and 296 subtests. Targeted comparison
found missing mixed-profile coverage, ordering mismatches, lost C85
provenance, an undocumented C86 status, and a C89 rejection mismatch.

### Follow-up implementation verification

C87's exact translated shape renderer passed four Lean cases using the
published Atom shape. Lean rejected a field substitution. C88's exact
translated entry passed the three ordered comparisons to its worker.
Lean rejected a missing comparison.

C86 rejects malformed bounds and body values from Lean. The exact
translated predicate passed nine Lean cases and rejected a mutation
that accepted byte 256. The published Contract's witness array matched
133 observed inputs in one C30 framing comparison.

C95 now requires the same Project-relative pins for files and ingested
snapshots. Both verifier modes reported the same exact Active sources
and rejected an absolute Manifest pin.

Other renderer profiles, full translated C86, C88, and C95 execution,
and external effects remain unresolved.
