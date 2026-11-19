---
atom_id: CA-R-1246
ref_id: CA-R-1246
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Relation
  dependencies:
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Projection/(.Form:=Applicable Methodology)
  - ANECHOIC_MODEL <+ Projection
tier: 1
status: Active
version: 34
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-R-1246-CORE_META_MODEL-RULE--keep-relation-vocabularies-graph-specific.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1246-CORE_META_MODEL-RULE--keep-relation-vocabularies-graph-specific.md
  source_atom_id: CA-R-1246
  source_atom_revision: 34
  source_sha256: 3662d2bf56c1b4f57a5ae487056ddeedcb53ab229261df0acd9426c7dcbe4f78
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep relation vocabularies graph-specific

## Claim

### Prose Claim


Relation Types, their shared Project identities, and any applicable Entity Definition constraints in ANECHOIC Graphs.


Relation Type names are shared across ANECHOIC Graphs and unique within the Project. A Relation Type is not owned by a graph kind. Existing Entity Definition constraints, where applicable, supply graph-specific endpoint classes, endpoint graph contexts, cardinality, permissions, and prohibitions for that shared Type. They do not create graph-owned Type copies or impose a new per-Type/per-graph admission registry; this contract chooses neither default allow nor default deny.

instances of the same graph kind governed by the same Applicable Methodology **must** reuse the same defining Relation Type authority and any applicable Entity Definition constraints. Matching names identify the shared Type; they do not create interchangeable copies or erase graph-specific constraints.

where an Entity Definition constraint applies, it determines graph-specific endpoint constraints, **not** a requirement that all endpoints occupy the same graph. admitted cross-graph endpoints and source references under CA-R-1472 retain their endpoint identity and source traceability. another graph **may** represent a source-traceable reference **or** view of the Relation **without** creating a graph-specific Type copy.
