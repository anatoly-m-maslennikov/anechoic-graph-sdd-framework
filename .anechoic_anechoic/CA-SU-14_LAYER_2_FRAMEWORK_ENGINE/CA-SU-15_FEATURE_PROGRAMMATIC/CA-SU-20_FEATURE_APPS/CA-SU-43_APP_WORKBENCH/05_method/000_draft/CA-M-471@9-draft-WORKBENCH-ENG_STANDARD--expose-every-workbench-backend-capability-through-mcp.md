---
identity:
  atom_id: CA-M-471
  ref_id: CA-M-471@9-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Method
  form: Eng Standard
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
  tier: 4
relations:
  method_for:
  - CA-R-2728
  - CA-R-2729
  - CA-R-2776
  - CA-R-2727
  IS_REPLACEMENT_FOR:
  - CA-M-471
state:
  status: draft
  version: 9
  updated_at: '2026-11-14T07:53:07.557473+00:00'
destination:
  file:
    name: CA-M-471@9-draft-WORKBENCH-ENG_STANDARD--expose-every-workbench-backend-capability-through-mcp.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/05_method/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Expose every Workbench backend capability through MCP

## Claim

### Prose Claim

Implement Workbench backend capabilities once. Web and MCP expose the same
arguments, results, errors, saved URLs, and shared Workspace and View state.

## Details

- Browser preferences and local drafts stay in the browser.
- Use Run with Save for Bookmarks and View Save for saved Views.
- Share result delivery and explicit SQL reads across both adapters.
- Native Codex chat owns conversation control.
