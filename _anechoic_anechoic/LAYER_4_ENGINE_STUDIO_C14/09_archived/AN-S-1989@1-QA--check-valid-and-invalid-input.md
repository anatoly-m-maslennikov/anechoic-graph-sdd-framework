---
atom_family: SPEC
atom_id: AN-S-1989
container:
  component: C14
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: '2026-11-11T17:28:27.098061+00:00'
---
## Summary

Check valid and invalid input

## Claim

### Prose Claim

Check how an Engine operation behaves with each applicable input case.
- valid input.
- valid fields and one or more wrong values.
- valid fields and one or more missing required values.
- wrong and missing values together when both can occur in one request.

Where the operation accepts corrections, check that valid fields are retained and that submitting only the requested corrections can complete the operation.
