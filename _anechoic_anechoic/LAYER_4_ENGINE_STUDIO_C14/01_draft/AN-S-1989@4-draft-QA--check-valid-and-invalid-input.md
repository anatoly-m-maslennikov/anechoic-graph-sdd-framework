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
  version: 4
  updated_at: '2026-11-14T08:20:28.205897+00:00'
---
## Summary

Check valid and invalid input

## Claim

### Prose Claim

Check valid input, wrong values with valid fields, missing required values
with valid fields, and combined wrong and missing values where applicable.

## Details

### Where corrections are accepted

- Check field errors, retention of recognized valid fields, reporting of
  unknown fields, and corrected fields sent alone or with additional input.
- Use the exact live Workflow Run ID. Check that MCP returns field errors
  to the AI Agent without an Operator form.

### Cancellation and failure

- Cancel at each pre-write correction stage. Verify that it clears the
  pending request without changes.
- After a write, verify that failure reports completed effects and ends
  the request.
