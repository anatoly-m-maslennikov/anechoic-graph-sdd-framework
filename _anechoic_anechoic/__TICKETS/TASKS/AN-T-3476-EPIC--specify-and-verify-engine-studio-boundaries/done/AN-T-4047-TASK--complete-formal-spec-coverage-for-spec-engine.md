---
atom_family: TKT
atom_id: AN-T-4047
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:07:31.594078+00:00"
---
## Summary

Complete formal Spec coverage for Spec Engine

## Scope

Cover C75, Source Adapters, Formal Model, Project Structure, Formal
Specification, and their in-scope Components and Seeds. Use the published
C50 Formal Model Generator interface as an input. C50 and its Seeds,
including CS1 Manifest Compiler, are outside this Task. Include the
interfaces to startup, ingestion, and the Database Server.

## Acceptance

- Inventory the Components and Seeds from Project Structure. Record the
  exact Manifest and Solution refs and verification result for each.
- Complete formal Boundaries and embedded Contracts for each Component.
  Cover Code Access, Process, State, and I/O where they apply. Add or
  update the Tier 0 Solution that ANSWERS each Manifest. Keep each Seed's
  formal interface and Solution in its Manifest.
- Validate the declarations and eDSL to Lean translation. Compare each
  Manifest and Contract with its Solution, each parent Solution with
  its children's Contracts, and the Contracts at sibling handoffs.
  Resolve conflicts and report any unsupported obligations explicitly.
- Cover the compiled Model fallback and bind the same pinned Spec snapshot
  through the managed flow. Review Solutions at 45 nonblank lines or more
  for delegation. Reuse existing Components and Seeds where they fit.

## Evidence

Draft Manifests and linked Tier 0 Solutions cover the 16 in-scope
Components. The comparison evidence includes managed and offline Structure
entries, the bootstrap fallback, validation and bounded framing, and exact
child Manifest pins. The group and shape checks cover C51 and C52.

Lean still needs external evidence for exact call arguments, receipt
provenance across runtime boundaries, and Code Access, State, and I/O
obligations outside its supported profiles. The source and digest ledger is
`spec-engine-formal-inventory.json` in the session evidence.

The 45-line review flagged C75, C84, C86, C93, and C94. Their longer
Solutions describe distinct entry points or existing child calls. The
review retained those owners. C93's reconciled Manifest is AN-S-5018@5
and its matching Solution is AN-S-5019@3, both Drafts.

The repeat review repinned C93's ANSWERS relation to AN-S-5018@5-draft.
It verified C53's current Draft pair and scoped Code Access for the
new C85 and C93 imports. Source pins and proof limits are in
`an-t-3476-repeat-review.md` in the session evidence.
