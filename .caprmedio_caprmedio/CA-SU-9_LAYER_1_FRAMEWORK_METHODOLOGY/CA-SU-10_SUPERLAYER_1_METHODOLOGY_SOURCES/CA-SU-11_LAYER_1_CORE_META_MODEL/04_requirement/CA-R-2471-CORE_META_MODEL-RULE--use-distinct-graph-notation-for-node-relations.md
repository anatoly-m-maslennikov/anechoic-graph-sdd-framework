---
atom_id: CA-R-2471
ref_id: CA-R-2471
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics
tier: 3
status: active
version: 11
updated_at: '2026-11-12T02:58:44.805499+00:00'
carrier_destination:
  file:
    name: CA-R-2471-CORE_META_MODEL-RULE--use-distinct-graph-notation-for-node-relations.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Use distinct graph notation for Node relations

## Claim

### Prose Claim

Treat a Topic as a reference to its declared target. Use the notation in CA-R-1321 and the namespace boundary in CA-R-2483.

- MODEL identifies declared kinds and Properties. Inheritance reuses the original Property Declaration.
- STRUCTURE identifies objects by containment. Containment preserves each object's identity.
- A reverse writing expresses the same Relation fact with swapped endpoints. Each outgoing direction has its own applicable permission and bounds.
