---
atom_id: CA-R-2470
ref_id: CA-R-2470
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ (Node, Node.**)
tier: 3
status: active
version: 3
updated_at: '2026-11-14T07:31:37.260174+00:00'
carrier_destination:
  file:
    name: CA-R-2470-CORE_META_MODEL-RULE--inherit-declaration-constraints-and-enforce-relation-whitelists.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Inherit Declaration constraints and enforce Relation whitelists

## Claim

### Prose Claim


For Node1/Node2, Node2's instances receive Node1's applicable:

- Relation cardinalities.
- Declared Properties.
- Property Formats and value domains.
- Direct-value and nested-Property cardinalities.

Applicable local Node constraints also apply. Inheritance does not copy actual values or Relation facts. Reuse an inherited Property's Declaration; an inherited lookup creates no new Property or bearer.

A direct Relation is eligible when its declared endpoint pair matches. Apply the Node’s effective Entity constraints to that Relation. An inverse view requires explicit permission for its direction.

