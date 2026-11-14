---
identity:
  atom_id: CA-M-1028
  ref_id: CA-M-1028@1-draft
context:
  container:
    scope_unit: CA-SU-46
  role: Method
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development
      <+ Frontend Engineering <+ Code Style
    dependencies:
    - MODEL//CAPRMEDIO <+ Projection
    - CAPRMEDIO_STRUCTURE
  tier: 4
relations:
  method_for:
  - CA-R-2727
  IS_REPLACEMENT_FOR:
  - CA-M-467
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T20:51:01.763167+00:00'
destination:
  file:
    name: CA-M-1028@1-draft-WORKBENCH_FRONTEND-DECISION--structure-workbench-frontend-files-by-responsibility.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-46_FEATURE_WORKBENCH_FRONTEND/05_method/000_draft
current_scope_unit: WORKBENCH_FRONTEND
claim_target_scope_unit: WORKBENCH_FRONTEND
author: Anatoly Maslennikov
---
## Summary

Structure Workbench frontend files by responsibility

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Structure authored HTML, CSS, JavaScript, TypeScript and Svelte by responsibility. Splitting files above 300 lines is strongly recommended. Split files above 500 lines. These limits exclude generated build files, lockfiles, vendored sources and frozen history.

Start with a small reusable component palette. Separate components, stateful behavior and styles when their responsibilities differ. Do not add arbitrary wrappers or fragments to meet a line count.

Use Svelte to structure HTML. Use a Python HTML builder only when the selected frontend tools cannot structure it.
