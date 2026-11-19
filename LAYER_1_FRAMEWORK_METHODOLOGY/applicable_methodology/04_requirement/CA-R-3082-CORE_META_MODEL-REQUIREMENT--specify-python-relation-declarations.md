---
identity:
  atom_id: CA-R-3082
  ref_id: CA-R-3082
context:
  role: requirement
  form: requirement
  tier: 3
  container:
    scope_unit: CA-SU-11
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom.Content.Claim.Formal Claim
state:
  version: 3
  status: active
  updated_at: '2026-11-14T07:29:18.360406+00:00'
destination:
  file:
    name: CA-R-3082-CORE_META_MODEL-REQUIREMENT--specify-python-relation-declarations.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3082-CORE_META_MODEL-REQUIREMENT--specify-python-relation-declarations.md
  source_atom_id: CA-R-3082
  source_atom_revision: 3
  source_sha256: 3a80e778f9d31dfc47803955b368809ac6f54a5779ac9ce6d9e5be85fb48d05b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Specify Python relation declarations

## Claim

### Prose Claim

- Use `declare_relation` to specify the canonical name, the eligible Model kinds and levels at each endpoint, and any aliases. A matching endpoint pair admits the direct Relation.
- Use `endpoint_pairs` when each source domain admits a specific target domain. Give each pair a `source_endpoint` and a `target_endpoint`. The inverse reverses each pair.
- Declare an inverse alias against its canonical Relation. Its source and target slots swap. An explicitly admitted reverse view derives from the direct fact.
- Specify each endpoint's Model or instance level. Put cardinality and other conditions in the relevant Entity Declarations. Apply those constraints within the Relation's endpoint domain.
- Declare the inheritable contracts on `NARROWER_THAN`. Python class bases establish the narrowing path. Resolve schema rules through the class MRO and explicit MODEL overrides.

- A canonical Relation declaration has Direct classification by default.
- Endpoint address forms identify canonical Relations, inverse alias addresses, base Atom IDs, and exact represented-content versions. Resolve inverse alias addresses through canonical Relation metadata.
