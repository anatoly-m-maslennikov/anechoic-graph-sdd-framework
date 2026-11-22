---
atom_family: TKT
atom_id: AN-T-2060
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: canceled
  version: 1
  updated_at: '2026-11-20T20:35:37.546728+00:00'
---
## Summary

Public Release draft headings differ from its specification

## Claim

### Prose Claim

CA-M-366@19 and CA-E-612@18 name `What's new` and `What's fixed` as separate sections. `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release_materials.py` requires `## New` and `## Fixed`. A draft that uses the documented labels fails validation.
