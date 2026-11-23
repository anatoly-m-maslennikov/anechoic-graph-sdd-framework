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
  version: 6
  updated_at: 2026-11-04 17:55:47 +0400
---

## Summary

Execute one read-only DuckDB query

## Claim scope

One synchronous public Run, Page or Check request.

## Claim

Execute a read-only query through the Project's shared owner:

- serialize the request with source refresh;
- validate the request and admit one native read query for Run or Check;
- retain original ordered column metadata, materialize the accepted query once into an internal result table, and commit the trusted cache write;
- for Run, count that result and return its first bounded page with its query ID and exact counts;
- for Page, read the requested slice from the existing stable result without rerunning SQL;
- for Check, return exact counts and discard the internal result;
- return known SQL, page and delivery errors to the caller, and keep source diagnostics on stderr.

The Action does not edit source files or logical source facts. It adds no query job, queue, scheduler, retry, rollback, recovery or business Journal record.
