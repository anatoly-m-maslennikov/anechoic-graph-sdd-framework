---
atom_family: SPEC
atom_id: AN-S-2692
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Require exactly one immediate bearer for each dependent Entity occurrence

# Summary

Require exactly one immediate bearer for each dependent Entity occurrence

```yaml
graph_rule_type: cardinality
applies_to:
  node: "Entity/Node/Continuant/Selection//Dependent Entity Occurrences"
  relation_type: IS_BORNE_BY
  direction: outgoing
condition:
  other_endpoint:
    - Entity
  minimum: 1
  maximum: 1
```
