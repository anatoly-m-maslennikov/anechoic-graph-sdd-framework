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
  version: 4
  updated_at: '2026-11-27T06:27:52.898712+00:00'
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

### Pinned implementation comparisons

The C74 command accepts exact Manifest, Solution and implementation
SHA-256 pins. The C30 framing check matched 133 current witnesses and
found six distinct bounds mismatches in the historical CRLF
implementation. A stale pin stopped comparison.

The C90 check used Active AN-S-4937@2 and AN-S-5024@2. Autoform-translated
Lean matched the three declared value equalities on one input. A
wrong-field implementation and a changed Contract each gave a
conflict. An unchecked return branch leaves the Solution facts
unresolved.

The trace verifier requires a reachable explicit output before it
reports matching outcome obligations. Lean string emission rejects
unpaired surrogates. Regression controls cover both defects.

Further Studio implementation behavior and unobserved effects require
evidence. The C90 witness does not cover the separate verdict operation.

### Tool API branch coverage

C88 requires evidence from every provider dispatch branch to confirm a
precondition. The public verifier reports a match when both branches
agree, unresolved when evidence is missing, and a conflict when an
observation contradicts the Contract.

Lean evaluated five branch-merge cases from the exact translated C88
source. A mutation that accepted partial evidence failed the missing
branch case. All 36 focused functional tests passed. The full translated
Tool API projection remains unresolved at the unsupported set call.
