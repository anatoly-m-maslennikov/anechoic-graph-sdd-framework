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
  version: 9
  updated_at: '2026-11-25T17:33:00+00:00'
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
- C17 separates connector admission from observed results. The Drafts
  cover verified reads and writes, verified no-op, uncertain effects,
  and refusal before dispatch. The Workflow retains domain decisions.
- C34 checks dry-run, invalid registry, and empty registry without
  service effects. C37 checks the read-only Projection and source
  lineage, and rejects an invalid frontier without returning a Projection.
- C70 requires the Orchestrator replacement IDs in the rebuild result.
  The same effect matches in its Draft Manifest, Contract, and Solution.
  The cross-Component route and lifecycle checks retain their exact pins.
- C21 checks the delegated Tool result and the error response across
  all three Specs. A failed call cannot return a success result.
  The View Run, Workbench caller, and C70 checks still match.
- C30 checks exact framing prefixes and eight byte examples.
  C52 checks Atom Header and Content types and the Plan subtype.
  C53 returns a checked instance or a validation error without
  writing it. Its admitted-Model handoff from C50 still matches.
- Source edits changed several Draft hashes. The affected normalized
  formal declarations were compared with the prior evidence, and all
  48 selected chains recompiled against current pins.
- C50 matches the declared compiler entry and six logical Structure
  properties across all three Specs. Omitting the Seed Manifest
  reference conflicts. Exact CLI arguments and stream data remain open.
- C69 requires Model and Structure compilation before capture, and
  sealing before it returns the receipt. C68 matches the launch binding
  and relies on sealed artifacts. Other CLI modes remain open.
- All 48 compiled chains have a matching scoped check in each direction.
  Seven Components still need an accepted boundary before their Contracts
  and primary Solutions can be completed.
- C50 checks previous-image Model staging. The accepted image
  requires matching Claims and an unchanged staged inventory.
  The Structure output and admitted-Model handoff still match.
