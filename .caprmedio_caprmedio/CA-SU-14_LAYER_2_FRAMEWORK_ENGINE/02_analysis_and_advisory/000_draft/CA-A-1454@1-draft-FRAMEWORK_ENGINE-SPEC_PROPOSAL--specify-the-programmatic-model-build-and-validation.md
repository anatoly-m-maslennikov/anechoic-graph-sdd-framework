---
identity:
  atom_id: CA-A-1454
  ref_id: CA-A-1454@1-draft
context:
  role: analysis_and_advisory
  form: Spec Proposal
  tier: 3
  container:
    scope_unit: CA-SU-14
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//FORMAL_MODEL_ENGINE
state:
  version: 1
  status: draft
  updated_at: '2026-11-13T17:16:34.256039+00:00'
destination:
  file:
    name: CA-A-1454@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--specify-the-programmatic-model-build-and-validation.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft
---
## Summary

Specify the Programmatic Model build and validation

## Proposal

Build GENERATED_MODEL from the verified Python Formal Claims of the CAPRMEDIO_MODEL Declarations. Validate the complete selected set before generating the package. Use the generated classes and declared rules to validate a proposed instance at the write boundary.

## Rationale

The current code can inspect individual Python Claims and package one Scope Unit check. The Model build needs one verified set of Declarations with class inheritance, Property constraints and Relation contracts. The Model Projection reads the source Declarations for rule origins and overrides.

## Draft Atoms

- CA-M-1017@1-draft. Build Model classes with Python dataclasses.

## Current Atoms

- CA-R-3091, CA-R-3136, CA-R-3137, CA-R-3131, CA-R-2743.
- CA-M-1020. Reuse built-in Python capabilities.
- CA-E-828. Verify the generated Model build and instance validation.

## Review

Current Claims CA-R-2554 and CA-R-2708 declare named instance checks. Settle how the build publishes those checks under CA-R-3136 before promoting the remaining Method Draft.

## Work

CA-P-3058, CA-P-3059, CA-P-3055.
