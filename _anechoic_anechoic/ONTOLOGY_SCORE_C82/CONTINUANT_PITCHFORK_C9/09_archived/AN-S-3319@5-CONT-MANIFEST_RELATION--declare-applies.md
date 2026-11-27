---
atom_family: SPEC
atom_id: AN-S-3319
concern:
  subject: APPLIES
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T16:50:19.137094+00:00"
---

## Summary

Declare APPLIES

## Claim

### Prose Claim

A Tier 1 Applicable Principle applies a Tier 0 Axiom as a premise
within the scope of its Project Goal.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ApplicablePrinciple, Axiom, Relation

class Relation3319(Relation):
    name = 'APPLIES'
    relation.inverse_alias = 'IS_APPLIED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (ApplicablePrinciple,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (Axiom,)}
```
