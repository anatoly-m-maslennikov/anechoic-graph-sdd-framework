---
atom_family: SPEC
atom_id: AN-S-4328
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-07 17:10:31 +0400
---

## Summary

Verify Code Synopsis accuracy

## Claim

### Prose Claim

For a selected Code Synopsis:

1. Resolve its code locations in the stated Project context.
2. Compare its descriptive claims with the referenced code.
3. Check that documented rationale and inferred explanations are distinguishable.
4. Check an optional specification comparison against the cited specification.
5. Check the inherited Atom rules and declared Claim structure.

Use these cases:

- Legacy code without a specification: accept an accurate Synopsis.
- A supported code/specification difference: accept the neutral observation without requiring a Concern.
- An ambiguous or missing code location: report failed verification.
- A claim contradicted by the referenced code: report failed verification.
- Inferred rationale presented as a supported fact: report failed verification.

Record the result and evidence. Verification does not change code or create a Concern.
