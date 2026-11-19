---
atom_id: CA-R-1598
ref_id: CA-R-1598
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom
  dependencies:
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Carrier/File
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: Active
version: 25
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1598-CORE_META_MODEL-RULE--keep-every-atom-self-sufficient.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1598-CORE_META_MODEL-RULE--keep-every-atom-self-sufficient.md
  source_atom_id: CA-R-1598
  source_atom_revision: 25
  source_sha256: 1c05c0df45f62c094f2c605307bac3b76d96e90ceec063cd250870690a2fb5c3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep every Atom self-sufficient

## Claim

### Prose Claim


Atom Revisions and their applicable Properties.


**every** Atom Revision **must** carry its applicable Properties within its own Markdown Carrier so that its own declared content can be read **without** reconstructing it from a filename **or** directory placement.

- the applicable model determines which Properties are required, optional, **or** inapplicable; self-sufficiency does **not** invent missing Properties **or** permit an invalid value.
- a Relation **to** another Atom remains declared **only** on its registered owning endpoint; the other endpoint **and** inverse views are resolved from that declaration, **not** independently copied.
- self-sufficiency does **not** require copying the referenced Atom, governing model, **or** inherited Settings authority into this Atom.
