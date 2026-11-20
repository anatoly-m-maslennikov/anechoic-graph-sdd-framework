---
identity:
  atom_id: AN-T-2237
context:
  container:
    atom: AN-T-2483
  tier: 3
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-13T17:13:58.284862+00:00'
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
