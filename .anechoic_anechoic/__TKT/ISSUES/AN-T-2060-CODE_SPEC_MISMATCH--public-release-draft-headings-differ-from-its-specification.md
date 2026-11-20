---
identity:
  atom_id: AN-T-2060
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:54:03.059032+00:00'
---
## Summary

Public Release draft headings differ from its specification

## Claim

### Prose Claim

CA-M-366@19 and CA-E-612@18 name `What's new` and `What's fixed` as separate sections. `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release_materials.py` requires `## New` and `## Fixed`. A draft that uses the documented labels fails validation.
