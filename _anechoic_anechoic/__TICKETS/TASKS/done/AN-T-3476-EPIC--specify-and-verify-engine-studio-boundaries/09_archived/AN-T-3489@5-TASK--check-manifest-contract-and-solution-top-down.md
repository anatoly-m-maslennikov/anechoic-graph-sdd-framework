---
atom_family: TKT
atom_id: AN-T-3489
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-S-2481@25
  - AN-S-3057@3-draft
  - AN-S-4884@1-draft
  - AN-S-4885@1-draft
  - AN-S-3076@3-draft
  - AN-S-4888@1-draft
  - AN-S-4889@1-draft
  - AN-S-2397@5
  - AN-S-3045@25-draft
  - AN-S-4792@2-draft
  - AN-S-4793@2-draft
  - AN-S-3058@7-draft
  - AN-S-3307@3-draft
  - AN-S-3373@3-draft
state:
  status: archived
  version: 5
  updated_at: '2026-11-25T16:52:44+00:00'
---
## Summary

Check Manifest, Contract, and Solution top down

## Work

Use Lean to check Manifest→Contract, Manifest→Solution, and Contract→Solution for each in-scope Component. Report matches, conflicts, and unresolved checks separately.

Check for overlapping ownership across Studio, Release, and Setup.
Keep one owner per responsibility and link dependent Specs to that owner.
Recheck the affected chains after consolidating their claims.

## Acceptance

The report covers all three checks for every in-scope declaration, records the unresolved obligations with their source evidence.

## Findings

- C33's duplicate Workflow declarations are archived. C18 owns
  multi-target sequencing. The C35 Drafts cover one Atom Action.
  Lean checks that C18 resolves the owner before dispatch, requires
  confirmation before another Action, and stops on failure or
  uncertainty. The failure case retains prior effects. Dispatching
  after a stop or discarding completed effects produces a conflict.
  Exact target and source identity remain open.
- C35 requires one explicit target before Find, expected-state
  Check, and Change. The Draft Contract rejects invalid cardinality
  without a Change. Lean detects two targets, an implicit target,
  and Change before Check or after rejection. Exact selected Atom
  and Property values remain open.
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
- C15 defines the result of one Model Claim fence. Python returns
  compiled statements and CFEL returns statements without comments.
  Other languages return no Model statements. Compilation errors
  report a diagnostic and return no Model statements for that fence.
  Lean matches all three directions. Exact statement and diagnostic
  values remain open.
- C48 returns the selected bundled HTML or the Unknown UI resource
  error. Lean matches all three directions. URI selection, MIME and
  wire error values, listing, probe, and ping remain open.
- Lean detects seven violations of these two selected workflows,
  including returning statements for an unsupported language and
  returning HTML on the resource error path.
