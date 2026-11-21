---
atom_family: TKT
atom_id: AN-T-2016
container:
  component: C9
priority: 2
context:
  template: question
state:
  status: resolved
  version: 3
  updated_at: 2026-11-02 16:49:59 +0400
---
## Summary

How should CFEL test and set cardinalities?

## Question

How does CFEL distinguish allowed cardinalities, count tests and count conclusions?

## Resolution

CA-R-2243 and CA-R-2487 already define `{:n}` as an allowed cardinality, `{=n}` as a count test, and `{==n}` as a required or derived count conclusion.
