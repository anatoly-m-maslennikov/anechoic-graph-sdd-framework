---
atom_family: TKT
atom_id: AN-T-3923
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

Batch full DuckDB rebuilds in one transaction

## Baseline

The compact full-rebuild request measured 58.7 MiB. The Orchestrator
still sends one JSON request to the Kernel. Incremental DuckDB inserts
already use groups of 256 rows in both checkouts.

[Rebuild measurement](file:///Users/am/.bb/thread-storage/thr_86zjijbcaj/generation-title-measurement.json)

## Work

Have Workers prepare batches of complete rows at about 10 MiB each from
one source snapshot. The Kernel loads the batches and publishes the
rebuilt index in one DuckDB transaction. Readers see one complete
generation.

## Acceptance

Measure batch sizes during a fresh full rebuild on the target. Verify
that readers see the prior generation until publication and that a
failed batch leaves the prior generation available. Verify a
watcher-driven update and a Model-affecting lifecycle change. Check
Package `IMPORTS` edges, Project Structure, and last-good Model behavior.

## Progress

The main checkout stages full rebuild rows in a pinned artifact. Kernel
verifies it before its existing transaction. Delta admission uses the
existing path.

Kernel still assembles all frames in memory for cross-row validation.
Direct DuckDB staging remains open. Preserve artifact verification,
cross-batch validation, and atomic publication when loading frames.

A host rebuild on the target Studio indexed 7,001 rows from a 71.04 MiB
artifact. The largest frame was below 10 MiB. A watcher edit reached
SQL through a native delta. A forced error inside admission preserved
the previous generation.

Activating IMPORTS in a disposable Project triggered a batched rebuild.
A later invalid declaration produced a diagnostic while SQL kept the
last-good Model and Structure. After the Beta port, the whole-Project
Realization Graph and import lint found zero import violations.

The live Archive job timed out. Status remains in queue.

`$BB_THREAD_STORAGE/an-t-3923/host-batch-check-7000.json`
`$BB_THREAD_STORAGE/an-t-3923/batch-transaction-confirmation.log`
`$BB_THREAD_STORAGE/an-t-3923/host-batch-check-model.json`
`$BB_THREAD_STORAGE/an-t-3923/import-audit-final/receipt.json`
