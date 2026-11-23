---
identity:
  ref_id: CA-E-804@6-draft
  id: CA-E-804
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//ANECHOIC <+ Relation
  tier: 7
relations:
  evaluation_for:
  - CA-M-509
  IS_REPLACEMENT_FOR:
  - CA-E-804
state:
  status: draft
  version: 6
  updated_at: '2026-11-13T22:33:03.971381+00:00'
destination:
  file:
    name: CA-E-804@6-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-relation-registry-delivery-on-every-image-rebuild.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
author: Anatoly Maslennikov
---
## Summary

Verify relation registry delivery on every image rebuild

## Claim

### Prose Claim

Verify that the selected relation registry reaches the image unchanged through every supported build entry point, including Local Release.

#### Build modes

- Refresh mode compiles the registry before image assembly. A selected Declaration change changes the asset and build identity. Identical inputs yield identical bytes. Compilation failure stops the build.
- Existing mode uses the checkout registry unchanged. A missing asset stops the build. Verify with the ANECHOIC service stopped and no predecessor image.

#### Delivery and runtime

Verify source IDs, Versions, paths and fingerprints in delivered metadata. Project authority carriers remain outside the image context. Verify the installed runtime uses the packaged registry and a Declaration change takes effect after asset refresh and image rebuild.
