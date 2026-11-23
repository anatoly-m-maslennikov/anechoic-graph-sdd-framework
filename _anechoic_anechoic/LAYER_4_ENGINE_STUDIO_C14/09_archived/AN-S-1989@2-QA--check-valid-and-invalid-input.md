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
  version: 2
  updated_at: '2026-11-12T12:29:32.964989+00:00'
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

Where the operation accepts corrections, check that it returns field errors to the caller, retains valid fields, and accepts corrected fields alone or with additional input. For MCP, check that the AI Agent receives the errors in the response without an Operator form.

Check cancellation at each stage that can wait for correction before a write. Cancellation clears the pending request without applying changes. After a write, check that a failure reports completed effects and ends the request.
