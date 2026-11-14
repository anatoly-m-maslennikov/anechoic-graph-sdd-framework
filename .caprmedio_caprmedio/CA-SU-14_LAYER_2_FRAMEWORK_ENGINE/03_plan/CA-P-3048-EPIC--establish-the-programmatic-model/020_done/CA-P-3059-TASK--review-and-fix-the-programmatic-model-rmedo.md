---
identity:
  atom_id: CA-P-3059
  ref_id: CA-P-3059
context:
  role: plan
  form: Plan
  label: Task
  tier: 3
  container:
    atom: CA-P-3048
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR
relations:
  IS_BLOCKED_BY:
  - CA-P-3058
state:
  version: 1
  status: done
  updated_at: '2026-11-13T17:13:58.284862+00:00'
destination:
  file:
    name: CA-P-3059-TASK--review-and-fix-the-programmatic-model-rmedo.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/03_plan/CA-P-3048-EPIC--establish-the-programmatic-model/020_done
---
## Summary

Review and fix the Programmatic Model RMEDO

## Work

Review and adopt the coordinated Drafts in CA-A-1454. Verify the Structure Projection and reference changes for CA-SU-50 and the new MODEL_VALIDATION Scope Unit before adopting the split. Record the Current Atom IDs for CA-P-3055.

## Approved decision

FORMAL_MODEL_GENERATOR builds GENERATED_MODEL from checked Python Formal Claims. MODEL_VALIDATION exposes runtime validation to Tools and Apps. Named checks are authored in their Declarations and supplied to MODEL_VALIDATION through a separate checks module outside GENERATED_MODEL.

## Adoption

Current: CA-R-3090@4, CA-R-3091@4, CA-R-3134@2, CA-R-3136@3, CA-R-3146@1, CA-R-3147@1, and CA-M-1017@1.

The Structure Projection resolves FORMAL_MODEL_GENERATOR (CA-SU-50), GENERATED_MODEL (CA-SU-52), and MODEL_VALIDATION (CA-SU-53) under MODEL. CA-R-3137 is in MODEL_VALIDATION. The repository check confirmed 45 Scope Units and verified the unaffected paths and Role/Form permissions. CA-P-3055 tracks implementation.
