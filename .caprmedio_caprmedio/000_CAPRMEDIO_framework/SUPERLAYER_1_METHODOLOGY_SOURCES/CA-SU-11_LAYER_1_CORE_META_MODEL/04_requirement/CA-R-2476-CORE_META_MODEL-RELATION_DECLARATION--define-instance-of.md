---
atom_id: CA-R-2476
ref_id: CA-R-2476
container:
  scope_unit: CA-SU-11
role: Requirement
form: relation_declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//INSTANCE_OF
tier: 3
status: active
version: 9
updated_at: '2026-11-13T20:36:43.416800+00:00'
carrier_destination:
  file:
    name: CA-R-2476-CORE_META_MODEL-RELATION_DECLARATION--define-instance-of.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define INSTANCE_OF

## Claim

### Prose Claim

The Host is an instance of the Target declared Model entity. A Property instance is borne by its data bearer and is an instance of its corresponding model Property, which remains borne by its model bearer. A Property instance has no independent Carrier; its bearer and kind Relations are distinct and may coexist.

HAS_INSTANCE is the inverse alias of INSTANCE_OF. Both writings identify the same fact, with endpoints reversed; the alias does not grant an endpoint permission or add a fact.

For a declared Model entity `x`, `$a[<x>] ((INSTANCE_OF)) x` is a generic example: `$a` selects an existing instance of `x`; bare `x` denotes that Model entity. The example does not create either participant.

### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name="INSTANCE_OF",
    source_endpoint={"level": "instances"},
    target_endpoint={"level": "model_entities"},
    inverse_alias="HAS_INSTANCE",
    written_alias="//",
)
```

## Semantics

INSTANCE_OF relates an instance to its declared Model entity.
