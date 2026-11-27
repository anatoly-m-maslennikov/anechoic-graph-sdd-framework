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
  status: "archived"
  version: 1
  updated_at: '2026-11-23T23:29:53.000000+00:00'
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
