---
atom_family: SPEC
atom_id: AN-S-1360
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-06 20:37:19 +0400
---

## Summary

Verify Workbench on the current Project with a temporary Scope Unit.

## Claim scope

An explicitly selected live Project and its running Workbench backend.

## Claim

### Prose Claim

Run a canary against the current Project, in addition to disposable-fixture E2E tests:

- Record the selected Project, backend version and measured visibility timings for every operation.
- Create an isolated, uniquely named temporary Scope Unit tree with its Declarations and test Atoms.
- Exercise create, update, rename, move and delete for the temporary Atoms, checking query-visible identity, values and paths after each operation.
- Exercise create, update, rename, move and delete for temporary Scope Units, including updates to their actual Declarations and authority folders. Keep each published Declaration state valid; a Scope rename or move may replace its Declaration while natively moving its owned folder. Record these distinct events honestly.
- Query Workbench after each operation to verify the expected Scope Unit structure and source rows.
- Remove the temporary Scope Units, their Declarations and test carriers.
- Query Workbench until those temporary rows are absent.

Use the real source readers, watcher and query interface. Do not substitute mocked data or a copied Project for this canary. Check the complete temporary Declaration before placing it in the watched tree. Remove only artifacts created by this run, including on failure, and report any cleanup that could not complete. Preserve unrelated files and concurrent work.

If any operation fails, stop the canary and clean up only its own artifacts. Keep the failure in the report.

Keep this canary separate from ordinary tests and require explicit live-Project selection before it can write. Report failures and observed latency; do not invent a latency limit or claim that a live test used a newer backend than the version actually running.
