---
atom_id: CA-D-652
ref_id: CA-D-652
container:
  scope_unit: CA-SU-11
role: Delivery
form: Decision
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Tier
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom
  - CAPRMEDIO_MODEL <+ Atom.Header.Context.Tier
  - CAPRMEDIO_MODEL <+ Projection
tier: 4
relations:
  delivery_for:
  - CA-R-2706
status: Active
version: 13
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-D-652-CORE_META_MODEL-DECISION--omit-default-numeric-tier-tokens-from-filenames.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-652-CORE_META_MODEL-ENG_DECISION--omit-default-numeric-tier-tokens-from-filenames.md
  source_atom_id: CA-D-652
  source_atom_revision: 13
  source_sha256: 3ae66c082b89d65b23fae71f91a8468f77e84bda4d47539a98593012dcbaa0f3
  original_relations_sha256: 2488e66b9f98116516eb3fe3c37e9d47f64d301b745a3e46e2d4a0ea0b04836c
---
## Summary

Omit Default Numeric Tier Tokens from Filenames

## Claim

### Prose Claim


Atom filenames whose registered grammar omits the default numeric Tier token.


an Atom filename **may** omit the default Tier `3` token only where the registered filename grammar explicitly defines that omission. The Atom **must** still carry its numeric Tier internally under CA-R-2706; omission **must not** add, remove, or alter an Atom Property, infer a Content Role or Type restriction, or change the represented source Properties in a Projection or other non-Atom Artifact. A Project Goal's explicit Tier `-1` grammar is evaluated before any ordinary default omission.
