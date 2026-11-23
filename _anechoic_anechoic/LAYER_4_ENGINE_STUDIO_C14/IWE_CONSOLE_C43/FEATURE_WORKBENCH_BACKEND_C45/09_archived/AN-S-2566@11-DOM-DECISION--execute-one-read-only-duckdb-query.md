---
atom_family: SPEC
atom_id: AN-S-2566
container:
  component: C45
tier: 6
context:
  template: DECISION
  lens: DES/DOM
state:
  status: archived
  version: 11
  updated_at: 2026-11-10 00:46:37 +0400
---

## Summary

Execute one read-only DuckDB query

## Operation

### Claim scope

One synchronous public Run or Check request.

### Claim

Execute one whole read-only Run or Check through the selected Project's shared owner:

- validate the whole query and its arguments; a cursor is editor metadata only;
- serialize execution with source refresh and admit one native read query;
- materialize it once and retain its original ordered column metadata;
- for Check, return validity and available exact counts or errors, then discard its internal result; do not export, save, log or echo SQL;
- for Run, retain the query ID and exact counts; save a Bookmark synchronously only when requested and only after execution succeeds;
- submit the Run's metadata-only history to the existing background writer without waiting for its file write;
- for a direct Run, export its complete cached result in the chosen format by default, or return an explicitly requested inline page; View Run returns metadata and leaves fetching to its separate operation;
- return a complete result-file descriptor only after writing succeeds. On later export or save failure, preserve the completed cached result and report the failed part without retry or rollback;
- omit full SQL from ordinary execution and result-fetch responses; return source diagnostics on stderr and useful query errors to the caller.

For a View rerun, validate the request before releasing its old result. Once valid execution begins, release the old result before running the new query. A later native-query failure leaves no old result. Editing SQL alone does not release the last result. The existing lifecycle owns result retention and View pinning.

Page and View Fetch read the existing cache. They export the requested bounded page by default or return explicitly requested inline rows. They never execute SQL again, save SQL or append a Run log. Explicit Load and View-query reads still return SQL.

This operation does not edit source Atoms or Scope Units. It adds no job, query queue, scheduler, retry, rollback or recovery.
