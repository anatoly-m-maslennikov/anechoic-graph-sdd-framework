---
identity:
  atom_id: CA-M-1025
  ref_id: CA-M-1025
context:
  role: method
  form: Implementation Method
  tier: 3
  topics:
    main_subject: ANECHOIC_MODEL <+ Projection
    dependencies:
    - ANECHOIC_MODEL <+ Atom.Content
    - ANECHOIC_MODEL <+ Atom.Content.Summary
  container:
    scope_unit: CA-SU-11
state:
  version: 1
  status: active
  updated_at: '2026-11-13T18:41:50.942682+00:00'
destination:
  file:
    name: CA-M-1025-CORE_META_MODEL-IMPLEMENTATION_METHOD--derive-navigation-values-from-authoritative-atom-content.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-1025-CORE_META_MODEL-IMPLEMENTATION_METHOD--derive-navigation-values-from-authoritative-atom-content.md
  source_atom_id: CA-M-1025
  source_atom_revision: 1
  source_sha256: 41a3858b14d27e5c0426591862f519382e94341f2328c5bb7271e0f3fd377200
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Derive navigation values from authoritative Atom content

## Claim

### Prose Claim

Derive an Atom's navigation values from authoritative content rather than another navigation value. For a new Atom, derive the Summary from its finalized primary contribution within its applicability. For RMED, use the Claim read within Scope, not Scope alone. Choose clear wording without adding authoritative meaning.

Derive each requested Translation or other Projection from its applicable complete source content, including relevant applicability restrictions, not from the Summary. For an existing Atom identity, retain its Summary and check source faithfulness. A needed Summary change follows the Atom identity rule; do not regenerate the Summary as an independent Projection.
