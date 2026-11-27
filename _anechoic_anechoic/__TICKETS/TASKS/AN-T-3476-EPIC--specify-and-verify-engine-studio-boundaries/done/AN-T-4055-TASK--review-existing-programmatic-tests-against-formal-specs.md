---
atom_family: TKT
atom_id: AN-T-4055
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-27T10:48:07+00:00"
---
## Summary

Review existing Programmatic tests against formal Specs

## Acceptance

Compare existing assertions with the applicable Contracts. Check whether mocks, fixtures, skips, and failure assertions can hide a mismatch. Fix confirmed test defects and rerun focused local checks.

## Evidence

Reviewed focused tests and requirements for the C15 Model Claim
compiler, C16 Tools, C19 Project Tools, C30 Adapters, and C49 Codex Hook.
Fixed a stale Ontology Score path in the C16 workflow fixtures. The C15
Form test now checks a valid input and the exact refusal diagnostic.

C19 now checks which Modules ran, each selection refusal, required skips,
Fast selection by whole Package, and the measured 45 and 46 line cases
in both Svelte script blocks. C49 now checks canonical worktree
resolution and verifies that denied inputs are not forwarded.

Focused Model, workflow, Hook, Adapter, and Project Tools checks passed.
All six changed files satisfy 45/300 and introduce no import findings
against the pinned Structure manifests. Four findings in these files
were already present.

The required host Functional registry includes 14 of the 164 in-scope
test modules outside C75. This review ran focused cases locally and
left release selection unchanged.
