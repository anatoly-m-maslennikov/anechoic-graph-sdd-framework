---
atom_family: TKT
atom_id: AN-T-3922
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-25T09:38:14.952756+00:00'
---
## Summary

Port the Beta rebuild fixes to the main checkout

## Source

Compare the on-disk meta-ontology worktree
`refactor/meta-ontology-dev-local` at `a6c3c108f1` with the main checkout
`amm/dev` at `b5f7ed5266`. Both checkouts have local edits. Select the
listed changes from the files and preserve unrelated changes.

[File comparison](file:///Users/am/.bb/thread-storage/thr_86zjijbcaj/beta-checkout-comparison.json)

## Work

- C30/C68. Index only the title from each Atom Summary. Keep the full
  Summary in the Atom file. Compact full-rebuild JSON and trim the
  lifecycle Model response.
- C67/C71. Port the 128 MiB full-rebuild limit, bounded DuckDB disk
  spill, the `IMPORTS` label fix, and the Model diagnostics and Project
  Structure projections.
- C69. Port Manifest ingestion, diagnostics, and last-good Model
  fallback. Move the relevant former C70 behavior into C82 and C68.
  Preserve the target's newer watcher, readiness, and request checks.
- Carry over Active `AN-S-4861` (`IMPORTS`) and preserve Ready status for
  `AN-S-4865`, `AN-S-4866`, `AN-S-4868`, `AN-S-4870`, `AN-S-4872`,
  `AN-S-4874`, and `AN-S-4876`.

## Acceptance

On the target, run a fresh full rebuild, a watcher-driven update, and a
Model-affecting lifecycle change. Verify Package `IMPORTS` edges, Project
Structure, Model diagnostics, and last-good Model behavior.

## Progress

The target compiler uses Formal Claims. The eight relation declarations
now use that syntax with the target Package address. AN-S-4861 compiled
as Active with the expected endpoints and inverse. All eight passed a
separate Lean compile with Ready relations activated only in the fixture.
The target retains one Active and seven Ready declarations.

`$BB_THREAD_STORAGE/an-t-3922/relation-model-receipt.json`

The port keeps full Summaries in their carriers and indexes their titles.
It compacts full rebuild JSON, trims the lifecycle Model payload, bounds
DuckDB spill, and exposes Model diagnostics and Structure. A capture
that changes during the read stops before Model fallback.

The disposable target verified a full rebuild, a watcher delta, and
Model activation. An invalid follow-up preserved the last-good Model
and Structure. The Realization Graph and import lint found zero import
violations. The outer audit saw changes only to two ignored Finder
metadata files. Fresh Lean and the source language and size checks
passed.

The packaged cold startup emits Model and Structure timing events.
Focused delta tests accept metadata that settles before the guarded
read and reject changes after capture.

`$BB_THREAD_STORAGE/an-t-3922/whole-project/summary.json`
`$BB_THREAD_STORAGE/an-t-3923/host-batch-check-model.json`
