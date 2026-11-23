---
atom_family: SPEC
atom_id: AN-S-1746
container:
  component: C00
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Canonical decomposition conformance

## Claim

**every** canonical decomposition satisfies CA-M-447 **and** CA-R-642.

## Check

for **every** declared axis:

- enumerate the bounded universe; **and**
- classify **every** admissible member.

report **any**:

- missing universe **or** axis declaration;
- unclassified member;
- multiple same-axis assignments; **or**
- forced near match.

the check **must not** change the governed decomposition.

## Acceptance

pass **only** **when** no conformance issue is found.

## Failure

record **every** issue as a Concern against the narrowest owning scope.
