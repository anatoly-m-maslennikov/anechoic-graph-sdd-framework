---
atom_family: TKT
atom_id: AN-T-2483
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: done
  version: 1
  updated_at: '2026-11-20T20:28:02.049924+00:00'
---
## Summary

Establish the Programmatic Model

## Objective

Establish the MODEL Scope Unit directly under PROGRAMMATIC. It contains FORMAL_MODEL_GENERATOR, GENERATED_MODEL, and MODEL_VALIDATION. This Epic delivers the generator, generated package, and shared validation library. CA-P-3022 tracks adoption by Tools and Apps.

## Work

1. Adopt the Scope Unit Declarations and Delegations in CA-A-1454. Keep CA-SU-50 for FORMAL_MODEL_GENERATOR.
2. Review the RMEDO against the Model and Project Structure Projection specifications.
3. Compare the reviewed RMEDO with the current implementation.
4. Build the generated package and verify the validation library in CA-P-3055.
5. Review and adopt Relation applicability and Property ordering RMEDO in CA-P-3065.
6. Migrate the Relation Declarations in CA-P-3066.
7. Update the Engine and validator in CA-P-3067.
8. Regenerate and verify the complete Model in CA-P-3068.

## References

Scope Unit Atoms: CA-R-2654, CA-R-3090, CA-R-3091, CA-R-3133, CA-R-3134, CA-R-3135, CA-R-3136, CA-R-3146, CA-R-3147.

CA-P-3022 tracks CFEL retirement. The Model Declaration and error specifications are CA-R-2721, CA-R-3081, CA-R-3082, CA-R-3131, and CA-R-3137.
