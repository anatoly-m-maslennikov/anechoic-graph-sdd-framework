---
atom_id: CA-R-1437
ref_id: CA-R-1437
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Relation
  dependencies:
  - ANECHOIC_MODEL <+ Relation
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Projection
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Traceability"
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Journal
tier: 1
status: Active
version: 32
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1437-CORE_META_MODEL-RULE--keep-one-source-for-each-relation-fact.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1437-CORE_META_MODEL-RULE--keep-one-source-for-each-relation-fact.md
  source_atom_id: CA-R-1437
  source_atom_revision: 32
  source_sha256: 9a221428a2f24f874ae9a2b2204d65fd2ac5147e87aff81de59a9e83c11e0706
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep one source for each relation fact

## Claim

### Prose Claim


authoritative source declarations for Relation facts.


**every** independently authored Relation fact **must** have **`=1`** authoritative source declaration under Single Source of Truth. its representation **in** multiple ANECHOIC Graph views remains a reference **or** derived Projection of that declaration **without** creating another independently maintained source.

a Relation derived under admitted derivation authority **must** remain traceable **to** that authority **and** its authoritative input facts, including through upstream Projections. it does **not** require a fabricated direct source declaration for the derived result. this distinction **must not** weaken a Relation Kind's requirement for an explicit source fact **or** permit unsupported inference.
