---
atom_id: CA-D-296
ref_id: CA-D-296
container:
  scope_unit: CA-SU-11
role: Delivery
form: file_layout
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Role
  dependencies:
  - CAPRMEDIO_MODEL <+ Scope Unit
  - CAPRMEDIO_MODEL <+ Atom
  - CAPRMEDIO_MODEL <+ Carrier/Directory
tier: 3
status: active
version: 34
updated_at: '2026-11-12T19:34:39.244837+00:00'
carrier_destination:
  file:
    name: CA-D-296-CORE_META_MODEL-FILE_LAYOUT--materialize-content-role-directories-on-first-artifact.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-296-CORE_META_MODEL-FILE_LAYOUT--materialize-content-role-directories-on-first-artifact.md
  source_atom_id: CA-D-296
  source_atom_revision: 34
  source_sha256: 6a1cc105819170e1bb568631e430d1875d01f207b8388e5f78719b0b913c3e7d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Materialize Content Role Directories on First Artifact

## Claim

### Prose Claim

Within a Scope Unit, derive the Role folder from the Role Declaration selected by `Header.Context.Role`.

1. Pad its Role Order Number to at least two decimal digits.
2. Encode the canonical Role name in lowercase snake case.
3. Join the two parts with one underscore.

Create the folder when the first Atom needs it. The applicable Status and Container layout determines the remaining placement.

### Formal Claim

```python
placement_rules = ({"kind": "role_root"},)
```
