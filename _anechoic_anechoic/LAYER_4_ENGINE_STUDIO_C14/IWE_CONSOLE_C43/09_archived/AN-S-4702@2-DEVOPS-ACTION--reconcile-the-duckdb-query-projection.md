---
atom_family: SPEC
atom_id: AN-S-4702
container:
  component: C43
tier: 6
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---

## Summary

Reconcile the DuckDB query Projection

## Claim scope

Current and Draft Atom carriers excluding Archived carriers, and their Project-local in-memory DuckDB query Projection.

## Claim

Reconcile the DuckDB query Projection **means** the technical background indexing Action that reads Current and Draft Atom carriers, excluding Archived carriers, into memory and updates its derived Projection without changing source Atoms. Every Current status remains included. It is not a planner, scheduler, orchestrator, query job, ticket, or background query processor.

The Action must:

- parse YAML and Markdown through in-memory schema Projections of relevant current model Declarations, without a generic CFEL evaluator, prose interpreter, JSON file, or third public database table;
- derive the current Scope Unit inventory from Current Scope Unit Declarations only; a Draft Declaration remains queryable but does not establish a current Scope Unit;
- store direct Relations from source Atoms and materialize declared derived Relations in memory;
- rebuild affected materialized rows when a source or relevant Declaration changes, and include materialized Relations in each public row hash;
- apply each affected indexing batch transactionally, so no public query observes a half-batch state;
- exclude an invalid, unreadable, or unstable source capture with its owned rows, write its path, error, and available location to stderr, and continue with unrelated valid sources; and
- write actual indexed, removed, and excluded-source counts only to technical stdout.

The Action does not retain stale rows for an excluded source, treat a source-file error as deletion, repair a source, return diagnostics as query rows, or automatically resubmit a failed input. A later actual source or relevant Declaration change is new input. A failed transaction remains uncommitted, writes its technical failure to stderr, and returns no partial or successful result. The Action writes no business Journal record.
