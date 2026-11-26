---
atom_family: SPEC
atom_id: AN-S-1746
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: "archived"
  version: 22
  updated_at: "2026-11-25T21:52:28.306072+00:00"
---
## Summary

Canonical decomposition conformance

## Claim

### Prose Claim


**every** canonical decomposition satisfies CA-R-642.

## Check

for **every** declared axis:

- enumerate the bounded universe; **and**
- classify **every** admissible member.

report **any**:

- missing universe **or** axis declaration;
- an axis without exactly one discriminating question;
- parts at different abstraction levels;
- any assignment of a member outside the declared universe;
- unclassified member;
- multiple same-axis assignments; **or**
- forced near match.

the check **must not** change the governed decomposition.

## Acceptance

pass **only** **when** no conformance issue is found.

## Failure

record **every** issue as a Concern against the narrowest owning scope.
