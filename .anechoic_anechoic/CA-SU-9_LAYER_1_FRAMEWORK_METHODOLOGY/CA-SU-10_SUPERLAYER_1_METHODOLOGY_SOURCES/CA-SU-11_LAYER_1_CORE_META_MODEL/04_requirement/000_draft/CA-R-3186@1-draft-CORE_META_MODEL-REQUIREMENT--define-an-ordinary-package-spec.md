---
identity:
  atom_id: CA-R-3186
  ref_id: CA-R-3186@1-draft
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
  updated_at: '2026-11-18T22:05:07.161317+00:00'
destination:
  file:
    name: CA-R-3186@1-draft-CORE_META_MODEL-REQUIREMENT--define-an-ordinary-package-spec.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define an ordinary Package Spec

## Claim

### Prose Claim

An ordinary Package needs one PKG Spec Atom when its boundary is specified. The Atom records its stable package ID, a short Purpose, and a Contract, and belongs in the owning Component’s Spec Section. Use a lens allowed by that Component’s effective whitelist. The Spec Atom retains its own stable Atom ID when its lens or name changes; the package ID is separate from its descriptive name. Place the specified Package immediately under its Component Package in Realization and include the package ID in the directory name, for example `create_order_pkg3344`. An ordinary Package may later become a Component.

## Details

Acceptance: a PKG Spec in an owning Component’s Spec Section records package ID `pkg3344`, a short Purpose, and a Contract under an enabled lens; `create_order_pkg3344` is directly under the Component Package. Moving it beneath another ordinary Package fails the stated placement.

Sources: CA-A-1462@1-draft, CA-A-1463@1-draft. Task: CA-P-3083.
