---
identity:
  atom_id: AN-S-2566
context:
  container:
    component: C45
  tier: 6
  lens: DES/DOM
  template: DECISION
state:
  status: active
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Execute one read-only DuckDB query

## Operation

### Claim scope

One synchronous public Run or Check request.

### Claim

Execute one whole read-only Run or Check through the selected Project's shared owner: validate arguments (cursor is editor metadata), serialize with refresh, admit one native read query and materialize it once with ordered metadata. Check returns validity/available exact counts/errors then discards its result without export/save/log/SQL echo. Run retains ID/counts and saves a Bookmark only after successful execution; it submits metadata-only history to the existing writer without waiting.

Direct Run exports complete cached result in the chosen format by default or explicit inline page; View Run returns metadata and fetches separately. Return descriptor only after export succeeds. Later save/export failure preserves known cached result and reports the failed part without retry/rollback; ordinary responses omit full SQL and source diagnostics go to stderr. Validate View rerun before releasing its old result; once execution begins release it even if SQL fails, while SQL editing alone preserves the last result. Page/View Fetch use existing cache only, never execute/save/log SQL; explicit Load/View-query reads return SQL. This action edits no source Atom/Scope Unit and adds no job, queue, scheduler, retry, rollback or recovery.
