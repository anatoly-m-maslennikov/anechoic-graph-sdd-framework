---
atom_id: CA-R-2525
ref_id: CA-R-2525
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Package
tier: 3
status: active
version: 5
updated_at: '2026-11-13T22:57:24.985880+00:00'
carrier_destination:
  file:
    name: CA-R-2525-CORE_META_MODEL-DECLARATION--declare-package.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---

## Summary

Declare Package

## Claim

### Prose Claim

Each Package other than a Project Package has exactly one IS_CONTAINED_BY link to a Package.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Continuant

class Package(Continuant):
    pass

declare_entity(
    entity_name="Package",
    entity_class=Package,
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {
            "target_entity_paths": ("Package",),
            "targets_per_source": Cardinality(minimum=0, maximum=None),
        },
        "IS_CONTAINED_BY": {
            "target_entity_paths": ("Package",),
            "targets_per_source": Cardinality(minimum=0, maximum=1),
        },
    },
)
```

## Semantics

A logical collection of implementation and documentation parts.
