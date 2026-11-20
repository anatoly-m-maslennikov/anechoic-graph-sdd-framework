---
identity:
  atom_id: AN-S-2609
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-14T07:31:37.260174+00:00'
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

