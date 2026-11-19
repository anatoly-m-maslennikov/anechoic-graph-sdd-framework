---
atom_id: CA-R-1471
ref_id: CA-R-1471
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity
  dependencies:
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Journal
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: Active
version: 27
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1471-CORE_META_MODEL-RULE--keep-secondary-graphs-derived-from-source-authority.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1471-CORE_META_MODEL--keep-secondary-graphs-derived-from-source-authority.md
  source_atom_id: CA-R-1471
  source_atom_revision: 27
  source_sha256: 22e17b352984e9e731fe4a163a1d6dc27ab3f33ef711f610be4e4740f3b2898d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep secondary graphs derived from source authority

## Claim

### Prose Claim


secondary ANECHOIC Graphs.


secondary ANECHOIC Graphs **must** be Projections derived from their selected authoritative sources **or** source-traceable upstream Projections. their nodes **and** Relations **must** preserve source identities **and** traceability **to** the governing derivation authority **and** source facts.

storing, composing, filtering, **or** rebuilding a secondary graph **must not** make its contents another source of authority. a represented source fact is corrected **at** its authoritative source; an incorrect derivation is corrected under its governing methodology. neither case is resolved by independently editing the projected fact **or** fabricating source history.
