---
identity:
  atom_id: CA-A-1454
  ref_id: CA-A-1454
context:
  role: analysis_and_advisory
  form: Spec Proposal
  tier: 3
  container:
    scope_unit: CA-SU-14
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//MODEL
state:
  version: 1
  status: active
  updated_at: '2026-11-13T17:16:34.256039+00:00'
destination:
  file:
    name: CA-A-1454-FRAMEWORK_ENGINE-SPEC_PROPOSAL--specify-the-programmatic-model-build-and-validation.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory
---
## Summary

Specify the Programmatic Model build and validation

## Proposal

MODEL has three parts:

- FORMAL_MODEL_GENERATOR validates the complete selected ANECHOIC_MODEL Declarations and builds the Python Model. It keeps the existing CA-SU-50 identity.
- GENERATED_MODEL contains the generated Python imports, classes and object construction.
- MODEL_VALIDATION is the shared library Tools and Apps call to validate complete proposed instances before writing. Named checks stay in their source Declarations and are made available through a separate checks module outside GENERATED_MODEL.

## Rationale

The generator needs a verified Declaration set with class inheritance, Property constraints and Relation contracts. The Model Projection reads source Declarations for rule origins and overrides. The validation library applies the Model to proposed instances.

## Adopted Atoms

- CA-R-3090@4 and CA-R-3091@4. Rename the existing generator Scope Unit and define its responsibility.
- CA-R-3134@2 and CA-R-3136@3. Define the MODEL split and the GENERATED_MODEL package boundary.
- CA-R-3146@1 and CA-R-3147@1. Declare and delegate MODEL_VALIDATION.
- CA-M-1017@1. Build Model classes with Python dataclasses.

## Current Atoms

CA-R-3131, CA-R-3137, CA-R-2743, CA-M-1020, CA-E-828.

## Work

CA-P-3059 adopted the coordinated Scope Unit and specification changes. Workbench verifies all three units under MODEL. CA-P-3055 implements the generator, generated package, and validation library.
