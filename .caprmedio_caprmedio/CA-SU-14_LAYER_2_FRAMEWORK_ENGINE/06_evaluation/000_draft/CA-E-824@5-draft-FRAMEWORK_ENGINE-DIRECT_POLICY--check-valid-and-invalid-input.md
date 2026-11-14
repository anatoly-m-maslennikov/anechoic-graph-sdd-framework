---
identity:
  atom_id: CA-E-824
  ref_id: CA-E-824@5-draft
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
  version: 5
  status: draft
  updated_at: '2026-11-14T08:28:36.520463+00:00'
destination:
  file:
    name: CA-E-824@5-draft-FRAMEWORK_ENGINE-DIRECT_POLICY--check-valid-and-invalid-input.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/06_evaluation/000_draft
relations:
  IS_REPLACEMENT_FOR:
  - CA-E-824
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
