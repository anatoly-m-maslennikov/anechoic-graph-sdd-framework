---
atom_id: CA-R-2462
ref_id: CA-R-2462@8
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node
tier: 3
status: archived
version: 8
updated_at: '2026-11-13T22:57:24.985880+00:00'
carrier_destination:
  file:
    name: CA-R-2462@8-CORE_META_MODEL-DECLARATION--declare-node.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/099_archived
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Declare Node

## Claim

### Prose Claim

In the selected effective MODEL, each logical model entity selected by Node or Node.** has exactly one outgoing IS_DECLARED_BY Relation to its qualified canonical declaring Requirement/Form Declaration Atom. This named outgoing permission applies to model entities, including Node Properties, and does not impose an ownership requirement on runtime instances. Derive the view only from a GOVERNS fact satisfying the declaring ownership qualification; do not store a second fact or infer any other inverse permission. The target-omitted bound counts each selected model entity’s outgoing links within the Relation Declaration’s qualified endpoint domain.

Atom Header and Content Property instances admit the sibling ordering Relation and its inverse alias under CA-R-2965.

Each Model Node or Property admits only explicitly permitted Relations, has at most one IS_PROPERTY_OF link, and has exactly one IS_DECLARED_BY link under the qualification above. A Model Property has exactly one IS_PROPERTY_OF link to its Node or Property bearer. A Model Node or Property with no bearer has Independence Primary Node; one with a bearer has Independence Property and no HAS_NARROWER links. Model Nodes and Properties have zero or more HAS_PROPERTY links to Model Properties; Model Properties have zero or more HAS_INSTANCE links to Property instances.

Node instances and their Properties admit only explicitly permitted Relations. Each instance Property has exactly one IS_PROPERTY_OF link to its Node or Property bearer and exactly one INSTANCE_OF link to its Model Property. Each Model Property has at most one instance per bearer. Node instances and their Properties have zero or more HAS_PROPERTY links to instance Properties.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity

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
