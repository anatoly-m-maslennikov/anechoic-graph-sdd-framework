---
atom_id: CA-R-2471
ref_id: CA-R-2471@8-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics
tier: 3
status: Draft
version: 8
updated_at: '2026-11-11 14:06:22 +0400'
carrier_destination:
  file:
    name: CA-R-2471@8-draft-RULE--use-distinct-graph-notation-for-node-relations.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Use distinct graph notation for Node relations

## Claim

### Prose Claim

Treat a Topic as a reference to its declared target. Use the notation in CA-R-1321 and the namespace boundary in CA-R-2483.

- MODEL identifies declared kinds and Properties. Inheritance reuses the original Property Declaration.
- STRUCTURE identifies objects by containment. Containment preserves each object's identity.
- A reverse writing expresses the same Relation fact with swapped endpoints. Each outgoing direction has its own applicable permission and bounds.
