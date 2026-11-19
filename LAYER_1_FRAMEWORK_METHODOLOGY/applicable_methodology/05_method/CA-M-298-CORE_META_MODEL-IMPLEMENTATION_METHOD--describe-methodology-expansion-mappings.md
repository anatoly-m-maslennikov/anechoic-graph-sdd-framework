---
atom_id: CA-M-298
ref_id: CA-M-298
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring"
  dependencies:
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_CONFIGURATION
  - ANECHOIC_STRUCTURE <+ Scope Unit//CORE_META_MODEL
tier: 2
relations:
  child_of:
  - CA-R-1375
  method_for:
  - CA-R-1375
status: Active
version: 27
updated_at: "2026-11-11 18:46:16 +0400"
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-298-CORE_META_MODEL-IMPLEMENTATION_METHOD--describe-methodology-expansion-mappings.md
  source_atom_id: CA-M-298
  source_atom_revision: 27
  source_sha256: 1d6e33c08f82a8992725a77339ea2bfb54b0a0a9fdcf22fa57f98c507a343c2c
  original_relations_sha256: 8bd15af5764c32dc1c5e420de77e90fac3418e6fddfad17bc2127235065a021b
---
## Summary

Describe methodology expansion mappings

## Claim

### Prose Claim


Methodology Source expansion mappings.


**to** describe a Methodology Source expansion mapping, use **`=1`** explicit mapping description that identifies:

- the source element **and** its provenance;
- the exact canonical target;
- the mapping rule;
- the intended scope of application;
- the applicable Core Meta-Model distinctions at **any** Local Tier.

apply this same mapping convention **to** Extension **and** Project Configuration sources regardless of provenance. the convention supports CA-R-1375-CORE_META_MODEL-CORE-REQUIREMENT--restrict-methodology-source-expansion-to-core-permission's expansion boundary; it does **not** admit activation **or** reliance. CA-O-054-CORE_META_MODEL-ACTION--admit-methodology-expansion-mappings owns that admission Action **and** re-evaluation following material changes.
