---
atom_family: TKT
atom_id: AN-T-3489
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T23:42:16.000000+00:00'
---
## Summary

Check Manifest, Contract, and Solution top down

## Work

Before AN-T-3485, use Lean to check Manifest→Contract, Manifest→Solution, and Contract→Solution for each in-scope Component. Report matches, conflicts, and unresolved checks separately.

Check for overlapping ownership across Studio, Release, and Setup.
Keep one owner per responsibility and link dependent Specs to that owner.
Recheck the affected chains after consolidating their claims.

## Acceptance

The report covers all three checks for every in-scope declaration, preserves unresolved cases, and is complete before AN-T-3485 implementation comparison begins.

## Findings

- C33's duplicate Workflow declarations are archived. C18 owns
  multi-target sequencing. The C35 Drafts cover one Atom Action.
  Lean matches all three directions for the observable outcomes in
  their new Draft Manifests. Exact target cardinality and other
  unmodeled semantics remain open.
- C81 owns image build and Project runtime launch. C63 owns Release
  installation. Lean checks the three stage owners and the
  symbolic candidate reference in the Local Release Drafts.
- C22, C23, and C54–C57 model the guidance carrier boundary.
  The Drafts distinguish guidance requirements from the work
  performed by the consuming agent.
- C14 models readiness after binding validation, pair readiness,
  and Current and Draft catch-up. An invalid Manifest has its own
  result and bars affected writes.
- C67 models one paired artifact response and the foreign-Project
  and no-generation results. Exact values, lock semantics, and
  Structure representation remain open.
