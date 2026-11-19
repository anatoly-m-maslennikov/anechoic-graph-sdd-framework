---
atom_id: CA-R-1502
ref_id: CA-R-1502
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node/Continuant
  dependencies:
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  - ANECHOIC_MODEL <+ Term//Property
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Method)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Delivery)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
tier: 1
relations:
  child_of:
  - CA-M-539
status: Active
version: 26
updated_at: "2026-11-11 18:46:16 +0400"
carrier_destination:
  file:
    name: CA-R-1502-CORE_META_MODEL--keep-authority-applicability-and-currentness-distinct.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1502-CORE_META_MODEL--keep-authority-applicability-and-currentness-distinct.md
  source_atom_id: CA-R-1502
  source_atom_revision: 26
  source_sha256: ac721376a63f752905c6b03d75dd47ee7df086c5554ab4b23aa0790e5226dd3d
  original_relations_sha256: 38ed74fc4f1cae0538794d8e7474a259e7d50dd0094a82b19b8d86817482a7d0
---
## Summary
Keep Authority, Applicability, and Currentness distinct

## Claim

### Prose Claim


an Artifact's Authority, Applicability, and Currentness Properties.


an Artifact's Authority, Applicability, **and** Currentness **must** remain distinct Properties under CA-R-1499, CA-R-1500, **and** CA-R-1501.

- an authoritative Artifact **may** be inapplicable **to** a given context.
- an applicable historical Revision **may** no longer be current.
- a current Projection **may** accurately report state **without** possessing semantic authority.

## Details

acceptance, provenance, Implementation, evidence, **and** Evaluation do **not** silently establish **any** of these Properties. precedence **and** conflict resolution select among **otherwise** authoritative **and** applicable Claims; they do **not** merge these Properties. the owning Requirement, Method, Evaluation, Delivery, **and** Operations Atoms govern how these Properties are resolved **and** reported through derived views.
