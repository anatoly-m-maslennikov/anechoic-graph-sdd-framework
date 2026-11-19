---
atom_id: CA-R-2462
ref_id: CA-R-2462
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Node
tier: 3
status: active
version: 9
updated_at: '2026-11-14T07:30:03.853470+00:00'
carrier_destination:
  file:
    name: CA-R-2462-CORE_META_MODEL-DECLARATION--declare-node.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2462-CORE_META_MODEL-DECLARATION--declare-node.md
  source_atom_id: CA-R-2462
  source_atom_revision: 9
  source_sha256: 43ba8358972d7ba03c510816c180028b5449dd2854d8229a44cc9c3dcf953e9c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Node

## Claim

### Prose Claim

In the selected effective MODEL, each logical model entity selected by Node or Node.** has exactly one outgoing IS_DECLARED_BY Relation to its qualified canonical declaring Requirement/Form Declaration Atom. This cardinality applies to model entities, including Node Properties, and does not impose an ownership requirement on runtime instances. Derive the view only from a GOVERNS fact satisfying the declaring ownership qualification; do not store a second fact or infer any other inverse permission. The target-omitted bound counts each selected model entity’s outgoing links within the Relation Declaration’s qualified endpoint domain.

Atom Header and Content Property instances derive their sibling ordering from their bearer's Property Declaration. A link joins Properties of the same immediate bearer. Each Property has at most one immediate predecessor and at most one immediate successor. The chain skips absent Properties and is acyclic.

Each Model Node or Property has at most one IS_PROPERTY_OF link, and has exactly one IS_DECLARED_BY link under the qualification above. A Model Property has exactly one IS_PROPERTY_OF link to its Node or Property bearer. A Model Node or Property with no bearer has Independence Primary Node; one with a bearer has Independence Property and no HAS_NARROWER links. Model Nodes and Properties have zero or more HAS_PROPERTY links to Model Properties; Model Properties have zero or more HAS_INSTANCE links to Property instances.

IS_PROPERTY_OF is acyclic. Each instance Property has exactly one IS_PROPERTY_OF link to its Node or Property bearer and exactly one INSTANCE_OF link to its Model Property. Each Model Property has at most one instance per bearer. Node instances and their Properties have zero or more HAS_PROPERTY links to instance Properties.

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
