---
atom_family: SPEC
atom_id: AN-S-2713
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 7
  updated_at: 2026-11-05 19:33:47 +0400
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
from anechoic.formal_claims import declare_relation

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
