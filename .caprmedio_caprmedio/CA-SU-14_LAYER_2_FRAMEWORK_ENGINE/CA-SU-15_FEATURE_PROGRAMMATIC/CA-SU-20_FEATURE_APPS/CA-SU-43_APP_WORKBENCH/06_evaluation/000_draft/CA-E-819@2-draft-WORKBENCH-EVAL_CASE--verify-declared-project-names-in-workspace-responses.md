---
identity:
  atom_id: CA-E-819
  ref_id: CA-E-819@2-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//CAPRMEDIO <+ Workspace
    - MODEL//CAPRMEDIO <+ Project
  tier: 5
relations:
  evaluation_for:
  - CA-R-2902
  - CA-D-673
  IS_REPLACEMENT_FOR:
  - CA-E-819
state:
  status: draft
  version: 2
  updated_at: '2026-11-14T07:53:00.795676+00:00'
destination:
  file:
    name: CA-E-819@2-draft-WORKBENCH-EVAL_CASE--verify-declared-project-names-in-workspace-responses.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Verify declared Project names in Workspace responses

## Claim

### Prose Claim

Verify that HTTP and MCP Workspace Open and Get return the declared Project
name without persisting it in Workspace documents.

Use a Project whose declared name differs from its directory basename.
Check `project_name` in both responses and inspect the saved Workspace.
