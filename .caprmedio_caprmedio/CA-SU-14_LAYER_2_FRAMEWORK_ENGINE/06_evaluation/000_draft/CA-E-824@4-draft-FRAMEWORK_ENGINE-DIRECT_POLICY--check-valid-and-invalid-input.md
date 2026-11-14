---
identity:
  atom_id: CA-E-824
  ref_id: CA-E-824@4-draft
context:
  role: evaluation
  form: direct_policy
  tier: 3
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Quality
      <+ Verification <+ Test Design
  container:
    scope_unit: CA-SU-14
state:
  version: 4
  status: draft
  updated_at: '2026-11-14T08:20:28.205897+00:00'
destination:
  file:
    name: CA-E-824@4-draft-FRAMEWORK_ENGINE-DIRECT_POLICY--check-valid-and-invalid-input.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/06_evaluation/000_draft
relations:
  IS_REPLACEMENT_FOR:
  - CA-E-824
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
