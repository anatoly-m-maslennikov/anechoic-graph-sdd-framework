---
atom_family: SPEC
atom_id: AN-S-2950
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-06 19:30:28 +0400
---

## Summary

Declare declaration-qualified expression calls

## Claim

### Prose Claim

`<Kind>.p(a)` evaluates the expression for Property path `p` authored in the Declaration of `Kind`, using the bound participant `a`.

- `p` is relative to `Kind`.
- `a` satisfies the selected Kind and its qualifications.
- The call selects the expression authored in that Declaration, including when a narrower Declaration supplies another calculation for the same Property.
- The expression reads Property values from the same `a`.
- A missing or ambiguous expression is an error.

The call evaluates a value. It creates no instance or stored fact.
