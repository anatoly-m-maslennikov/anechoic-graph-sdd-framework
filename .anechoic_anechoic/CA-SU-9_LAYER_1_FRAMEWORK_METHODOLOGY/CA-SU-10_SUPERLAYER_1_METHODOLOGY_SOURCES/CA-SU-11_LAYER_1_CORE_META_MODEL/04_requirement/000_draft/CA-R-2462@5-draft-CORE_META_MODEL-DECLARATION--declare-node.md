---
atom_id: CA-R-2462
ref_id: CA-R-2462@5-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Node
tier: 3
status: Draft
version: 5
updated_at: 2026-11-05 16:33:24 +0400
carrier_destination:
  file:
    name: CA-R-2462@5-draft-CORE_META_MODEL-DECLARATION--declare-node.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
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
