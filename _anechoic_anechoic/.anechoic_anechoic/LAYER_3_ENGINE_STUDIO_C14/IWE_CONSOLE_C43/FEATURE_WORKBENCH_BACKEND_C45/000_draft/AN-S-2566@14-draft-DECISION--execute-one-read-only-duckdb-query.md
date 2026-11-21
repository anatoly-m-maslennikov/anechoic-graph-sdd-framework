---
atom_family: SPEC
atom_id: AN-S-2566
structure:
  container:
    component: C45
  tier: 6
context:
  template: DECISION
state:
  status: draft
  version: 14
  updated_at: '2026-11-13T22:31:38.171018+00:00'
---
## Summary

Execute one read-only DuckDB query

## Operation

### Claim scope

One synchronous public Run or Check request.

### Claim

Execute one whole read-only Run or Check through the selected Project's shared owner. Validate arguments; the cursor is editor metadata. Serialize with refresh, admit one native read query and materialize it once with ordered metadata.

Check returns validity, available exact counts and errors, then discards its result without export, save, log or SQL echo. Run retains ID and counts, saves a Bookmark only after successful execution and submits metadata-only history to the existing writer without waiting.

Direct Run exports the complete cached result in the chosen format by default or an explicit inline page. View Run returns metadata and fetches separately. Return a descriptor only after export succeeds. A later save or export failure preserves the known cached result and reports the failed part without retry or rollback. Ordinary responses omit full SQL; source diagnostics go to stderr.

Validate a View rerun before releasing its old result. Once execution begins, release it even if SQL fails. SQL editing alone preserves the last result. Page and View Fetch use only the existing cache; they never execute, save or log SQL. Explicit Load and View-query reads return SQL.

This Action edits no source Atom or Scope Unit and adds no job, queue, scheduler, retry, rollback or recovery.

## Details

### Proposal

Provisional. Keep the existing Temporary State dependency. Its exact legacy address has no matching Current Atom in the gathered context. Confirm the intended address before changing that dependency.
