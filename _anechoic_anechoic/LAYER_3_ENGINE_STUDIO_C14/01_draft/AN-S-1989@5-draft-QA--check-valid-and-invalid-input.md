---
atom_family: SPEC
atom_id: AN-S-1989
container:
  component: C14
tier: 3
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-14T08:28:36.520463+00:00'
---
## Summary
Check valid and invalid input

## Claim
### Prose Claim
Check valid input and each applicable invalid case. Test wrong values and missing required values with valid fields.
Test both errors together where possible.

## Details
### Corrections
When corrections are accepted, check field errors, retained recognized valid fields, reported unknown fields, and corrected fields alone or with additional input.
For a live Workflow Run, use the exact Run ID. Check that MCP returns errors to the AI Agent in the response without an Operator form.
### Cancellation and failure
Check cancellation at each stage that can wait for correction before a write. It clears the pending request without changes.
After a write, check that failure reports completed effects and ends the request.
