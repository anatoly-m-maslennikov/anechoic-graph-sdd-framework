---
identity:
  atom_id: CA-R-3171
  ref_id: CA-R-3171@1-draft
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
  updated_at: '2026-11-18T22:02:59.984663+00:00'
destination:
  file:
    name: CA-R-3171@1-draft-CORE_META_MODEL-REQUIREMENT--define-project-goal-and-manifest.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Project Goal and Manifest

## Claim

### Prose Claim

The Project Goal is the root Project Component’s Purpose. The Project Manifest
declares the Project and its configuration. Both are Tier −1 Spec Atoms
in SPEC. The native runtime selects one Active `project_manifest` carrier
and reads `name` and `prefix` from its formal Python Claim. The Manifest
supplies Project configuration with at most 20 parameters in total. Project Axioms are Tier 1 general SPEC premises; Applicable Principles are Tier 2 general SPEC guidance and stand independently of Contracts. Product Definition is optional when business intent needs its own section.

## Details

Acceptance: the Goal and Manifest are in SPEC at Tier −1; a Manifest with more than 20 parameters fails the stated size limit.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
