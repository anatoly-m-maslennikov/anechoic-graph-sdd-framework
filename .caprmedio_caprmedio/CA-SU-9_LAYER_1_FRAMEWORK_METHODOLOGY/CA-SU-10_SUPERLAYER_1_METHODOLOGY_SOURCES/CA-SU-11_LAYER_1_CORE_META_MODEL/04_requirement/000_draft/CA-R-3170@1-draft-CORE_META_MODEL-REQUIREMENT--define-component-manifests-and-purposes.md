---
identity:
  atom_id: CA-R-3170
  ref_id: CA-R-3170@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:02:57.528847+00:00'
destination:
  file:
    name: CA-R-3170@1-draft-CORE_META_MODEL-REQUIREMENT--define-component-manifests-and-purposes.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Component Manifests and Purposes

## Claim

### Prose Claim

A Component Manifest is a Tier 0 Spec Atom declaring the described child Component’s existence, stable ID, name, parent, and layer where applicable. Its settings resolve from that Manifest. A Component Purpose is a Tier 0 Spec Atom stating why the child exists, with responsibilities and obligations in its details. A child can start with a Manifest and add one Purpose later. The parent Component contains both in its own Component Spec Section; each identifies the child it describes. A local extension defining a new Component kind belongs in PMETA.

## Details

Acceptance: a Manifest-only child is valid; a Purpose and Manifest for a child reside in the parent Spec Section and identify that child.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
