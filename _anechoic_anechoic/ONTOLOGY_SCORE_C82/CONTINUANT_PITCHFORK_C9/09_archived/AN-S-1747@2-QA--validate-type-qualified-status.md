---
atom_family: SPEC
atom_id: AN-S-1747
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Validate Type-Qualified Status

# Summary

Validate Type-Qualified Status

## Scope

Artifacts and their applicable qualified Status model.

## Claim

the Evaluation **must** reject an Artifact **if** **any** applicable condition holds:

- **when** an explicitly defined Status model applies, its Status domain is resolved outside its complete qualified Type **or** Atom Content Role **and** Type path, its current Status cardinality **`!=1`**, its current Status is **not** an allowed value of that domain, a prior transition coexists as current Status metadata, **or** a second disposition axis duplicates Status.

**when** no explicitly defined Status model applies, absence of a Status is **not** a rejection.

the Evaluation **must not** substitute Active **or** Inactive for a missing, invalid, **or** ambiguous Status. an Artifact outside the applicable qualified Status model **must not** fail merely because it has no Status.

## Details
