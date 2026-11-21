---
atom_family: SPEC
atom_id: AN-S-2606
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 5
  updated_at: 2026-11-05 16:33:24 +0400
---

## Summary

Declare Node

## Claim

### Prose Claim

- Each Model Node and each of its Model Properties has exactly one outgoing IS_DECLARED_BY link to its canonical Requirement / Declaration Atom. Derive the link from a GOVERNS fact that identifies the canonical declaring Atom.
- Each Node or its Properties allow only the explicitly admitted Relations, separately for Model entities and instances.
- Each Property has exactly one bearer. Its bearer is a Node or a Property. A Node has no bearer.
- Each Model Node or Property has at most one IS_PROPERTY_OF link.
- A Model Node or Property with no bearer has Independence Primary Node. One with a bearer has Independence Property and no HAS_NARROWER links.
- Atom Header and Content Property instances admit IS_ORDERED_RIGHT_AFTER and IS_ORDERED_RIGHT_BEFORE between siblings, under CA-R-2965.
- Model Nodes and Properties have zero or more HAS_PROPERTY links to Node Properties.
- Each Model Property has zero or more HAS_INSTANCE links to instances of Properties.
- Each Model Node has zero or more HAS_INSTANCE links to Node instances.
- Node instances and their Properties have zero or more HAS_PROPERTY links to instance Properties.
- Each instance Property has exactly one IS_PROPERTY_OF link to its Node or Property bearer, and exactly one INSTANCE_OF link to its Model Property.
- Each Model Property has zero or one instance per bearer.
- Model Nodes and Properties, and their instances, admit HAS_ALLOWED_VALUE and HAS_VALUE_CONSTRAINT links.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

class Node:
    pass

declare_entity(
    entity_name="Node",
    entity_class=Node,
    model_relation_constraints={
        "IS_PROPERTY_OF": {"targets_per_source": 0},
        "IS_DECLARED_BY": {"targets_per_source": 1},
        "NARROWER_THAN": {"target_entity_paths": ("Node",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "HAS_NARROWER": {"target_entity_paths": ("Node",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "HAS_PROPERTY": {"targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
    instance_relation_constraints={
        "INSTANCE_OF": {"target_entity_paths": ("Node",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "HAS_PROPERTY": {"targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Node can be the Host or Target of a Relation.
