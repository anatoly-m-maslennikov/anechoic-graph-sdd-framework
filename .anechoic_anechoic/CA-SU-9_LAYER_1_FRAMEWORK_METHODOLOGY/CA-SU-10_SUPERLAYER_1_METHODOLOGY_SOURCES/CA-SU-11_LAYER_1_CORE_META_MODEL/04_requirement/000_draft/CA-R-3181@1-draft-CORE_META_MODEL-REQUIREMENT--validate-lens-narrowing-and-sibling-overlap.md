---
identity:
  atom_id: CA-R-3181
  ref_id: CA-R-3181@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:53.919864+00:00'
destination:
  file:
    name: CA-R-3181@1-draft-CORE_META_MODEL-REQUIREMENT--validate-lens-narrowing-and-sibling-overlap.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Validate lens narrowing and sibling overlap

## Claim

### Prose Claim

Lenses use the `narrower_than` relation; every other lens is narrower than SPEC. A broader lens and any selection of its narrower lenses may be enabled together, but a narrower lens is separately available only when listed in the effective whitelist. Enabled sibling lenses must have disjoint sets of detailed lenses. Reject a whitelist when enabled siblings overlap; do not infer overlap merely because a broader lens is enabled with one of its narrower lenses.

## Details

Acceptance: `[SPEC, DES, SWE]` is valid; `[SWE, SWD, QA]` is valid and does not enable omitted DevOps. Given DES expands to IO and DOM and SYS expands to SWE and DOM, `[DES, SYS]` is invalid because both contain DOM. The same lens expansion applies in every Component.

Sources: CA-A-1462@1-draft, CA-P-3081@1. Task: CA-P-3081.
