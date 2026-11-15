---
atom_id: CA-R-1697
ref_id: CA-R-1697
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation
tier: 1
relations:
  child_of:
  - CA-M-544
status: Active
version: 37
updated_at: 2026-11-11 15:00:27 +0400
carrier_destination:
  file:
    name: CA-R-1697-CORE_META_MODEL-RULE--bind-traceability-to-exact-claims-and-revisions.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1697-CORE_META_MODEL-RULE--bind-traceability-to-exact-claims-and-revisions.md
  source_atom_id: CA-R-1697
  source_atom_revision: 37
  source_sha256: 066d88e2ee384e7dcee7e440ae7668fcad7fd391ff6d817db75daf84d7f64c70
  original_relations_sha256: d35825eca971ddd65fbe11e6167650bbc190099b18899bf70c7a06e6ced9ec10
---
## Summary

Bind traceability to exact claims and revisions

## Claim

### Prose Claim


CAPRMEDIO traceability assertions.


**every** CAPRMEDIO traceability assertion **must** identify the exact governed claim revision on which a receiving artifact, implementation target, evaluation use, delivery action, operational observation, **or** other governed result relies.

## Details

the trace **must** preserve the source identity **and** accepted Revision, the receiving identity **or** stable target locator, the typed relation between them, the bounded scope **and** use, **and** the provenance needed **to** replay that relation. a relation **to** an artifact ID **without** its relied-upon revision is insufficient **after** the Atom has more than one accepted Revision.

Traceability records relationships; it does **not** transfer authority **or** prove correctness, execution, delivery, **or** currentness. secondary storage history **may** preserve Carrier evidence, while governed Journals preserve semantic relationships independently of that secondary history.
