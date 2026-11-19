---
atom_id: CA-R-1696
ref_id: CA-R-1696
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//CORE_META_MODEL
tier: 1
relations:
  child_of:
  - CA-M-261
status: Active
version: 38
updated_at: "2026-11-11 18:46:16 +0400"
carrier_destination:
  file:
    name: CA-R-1696-CORE_META_MODEL-RULE--keep-the-core-meta-model-implementation-neutral.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1696-CORE_META_MODEL-RULE--keep-the-core-meta-model-implementation-neutral.md
  source_atom_id: CA-R-1696
  source_atom_revision: 38
  source_sha256: af7f465d3d9f9a9af6772ac092614d9eb7e3a726f6a64ae58b089d0a875d596b
  original_relations_sha256: 94899af1df3add3533bb824b693365050895abf0a071adfe4339109a042cf4cb
---
## Summary

Keep the Core Meta-Model implementation neutral

## Claim

### Prose Claim


CORE_META_MODEL authority and its reusable model invariants and expansion boundaries.


CORE_META_MODEL authority **must** define reusable model invariants **and** expansion boundaries **without** hidden dependence on a programming language, LLM provider **or** model, agent host, operating system, repository host, package manager, database, deployment platform, **or** other replaceable implementation mechanism.

mechanism-specific obligations belong **to** the Scope that owns the mechanism. Extensions **and** PROJECT_CONFIGURATION **may** expand the model for their bounded use **without** rewriting its governing Claims.

CORE_META_MODEL **may** name a mechanism **only** **when** the mechanism itself is the explicit Entity governed by the Claim, such as a Carrier format, portability boundary, **or** external constraint; this reference **must not** make that mechanism a hidden prerequisite of unrelated model Claims.
