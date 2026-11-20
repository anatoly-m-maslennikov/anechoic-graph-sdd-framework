---
identity:
  atom_id: CA-M-472
  ref_id: CA-M-472@7-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Verification <+ Test Design
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 4
relations:
  IS_REPLACEMENT_FOR:
  - CA-M-472
  SPECIALIZES:
  - CA-M-424
  method_for:
  - CA-R-2727
  - CA-R-2728
  - CA-R-2776
state:
  status: draft
  version: 7
  updated_at: '2026-11-14T08:28:43.775259+00:00'
destination:
  file:
    name: CA-M-472@7-draft-WORKBENCH-DECISION--test-workbench-through-its-public-interfaces.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/05_method/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary
Test Workbench through its public interfaces

## Claim
### Prose Claim
Test Workbench through its real browser, MCP and HTTP interfaces.
Use Playwright with Chromium against the existing Workbench test container.

## Details
### Browser checks
Use the container's real backend. Skip the Vite development server.
Keep browser test dependencies in the frontend's development dependencies. Run checks without retries.
