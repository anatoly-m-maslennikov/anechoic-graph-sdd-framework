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
  version: 9
  updated_at: '2026-11-19T22:50:21.237199+00:00'
---

## Summary

Execute one read-only DuckDB query

## Claim scope

One synchronous public Run or Check request.

## Claim

Execute one read-only Run or Check query through the Project's shared owner:

- select the statement at optional UTF-16 `cursor_position` using native SQL tokenization, preserving quoted strings, comments and dollar-quoted strings;
- serialize the request with source refresh;
- validate the request and admit one native read query for Run or Check;
- retain original ordered column metadata, materialize the accepted query once into an internal result table, and commit the trusted cache write;
- for Run, count that result and return its first bounded page with its query ID, actual selected SQL and exact counts;
- for Check, return selected SQL and exact counts and discard the internal result;
- return known SQL and delivery errors to the caller, and keep source diagnostics on stderr.

Run and Check do not save SQL, append a saved-item Journal record or require the Journal writer to be writable. Page, explicit Save, Worksheet Save, Load, List and Schema follow their shared Workbench contracts outside this Action.

The SQL operation does not edit Atom or Scope Unit source files or logical source facts. Internal materialized query state is disposable cache. It adds no query job, queue, scheduler, retry, rollback or recovery.
