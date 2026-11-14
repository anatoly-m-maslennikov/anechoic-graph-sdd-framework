---
atom_id: CA-R-2511
ref_id: CA-R-2511@6-draft
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan)
tier: 3
status: Draft
version: 6
updated_at: '2026-11-11 14:06:22 +0400'
carrier_destination:
  file:
    name: CA-R-2511@6-draft-DECLARATION--declare-atom-role-plan.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Declare Atom/(.Role := Plan)

## Claim

### Prose Claim

Each Current Plan recursively contained by a Done or Canceled Plan has exactly one Status, either Done or Canceled.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Atom

class Plan(Atom):
    pass

declare_entity(
    entity_class=Plan,
    entity_name="Plan",
    qualification_property_path="Atom.Header.Context.Role",
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "IS_BLOCKED_BY": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "BLOCKS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Plan describes bounded intended work or an intended outcome.
