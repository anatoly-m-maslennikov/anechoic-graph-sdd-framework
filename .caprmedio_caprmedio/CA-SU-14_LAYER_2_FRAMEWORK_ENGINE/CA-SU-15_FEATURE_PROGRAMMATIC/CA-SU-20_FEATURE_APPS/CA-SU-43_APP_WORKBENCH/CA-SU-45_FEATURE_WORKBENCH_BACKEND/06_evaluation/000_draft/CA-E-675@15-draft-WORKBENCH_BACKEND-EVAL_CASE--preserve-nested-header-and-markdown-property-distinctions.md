---
identity:
  atom_id: CA-E-675
  ref_id: CA-E-675@15-draft
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Source Retrieval
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2726
  - CA-M-464
  - CA-D-672
  IS_REPLACEMENT_FOR:
  - CA-E-675
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T23:58:42.491073+00:00'
destination:
  file:
    name: CA-E-675@15-draft-WORKBENCH_BACKEND-EVAL_CASE--preserve-nested-header-and-markdown-property-distinctions.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim

### Prose Claim

Verify that Current-model-guided in-memory parsing of governed carriers
preserves nested Header and Markdown Property distinctions.

## Details

### Private parsing

- Preserve the complete body, including LF and CRLF, and keep parsed Header
  separate from Markdown.
- Distinguish missing, null, empty, scalar, list, map, false, and zero values.
- Reject duplicate YAML keys.
- Keep direct Markdown values separate from nested Properties.
  - Treat undeclared prose headings and headings in code fences as text.
  - Apply the declared parsing rules for Prose Claim and Formal Claim.

### SQL projection

- In Mode 1, check declared Header paths. In Mode 2, check all valid Header
  paths observed at cold start, including empty ones.
- In both modes, verify declared Content paths and values.
- Check full dotted snake_case paths without a wrapper or raw parser data.
  - Use `Header.Context.Plan` → `header.context.plan` as the nested case.
  - Reject ambiguous flattened paths.

### Declaration coverage

- Check valid Current and Draft fixtures across all Roles and applicable Forms.
  Preserve each section at its declared path.
- Check nested, inherited, and multiword paths. Verify that wildcard rules,
  finite name lists, and bracketed constraints only limit declared paths.
- Check Role, Form, and Property changes after refreshing the asset and
  rebuilding the image. Existing behavior must still pass.
  - Verify that the watcher and full reread leave the loaded schema fixed.
  - Verify that value and presentation edits stay incremental.
- Verify that only supported Formal Claim blocks contribute model facts.
