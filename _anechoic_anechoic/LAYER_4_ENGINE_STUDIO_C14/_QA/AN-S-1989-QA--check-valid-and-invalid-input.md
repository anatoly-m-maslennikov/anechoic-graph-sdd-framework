---
atom_family: SPEC
atom_id: AN-S-1989
container:
  component: C14
tier: 3
context:
  lens: QA
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:12:09.762722+00:00'
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

Where the operation accepts corrections, check that it returns field errors to the caller, retains recognized valid fields, reports unknown fields, and accepts corrected fields alone or with additional input. For a live Workflow Run, use the exact Run ID. For MCP, check that the AI Agent receives the errors in the response without an Operator form.

Check cancellation at each stage that can wait for correction before a write. Cancellation clears the pending request without applying changes. After a write, check that a failure reports completed effects and ends the request.
