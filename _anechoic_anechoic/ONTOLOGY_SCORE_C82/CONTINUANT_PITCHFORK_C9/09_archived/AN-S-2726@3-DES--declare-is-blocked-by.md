---
atom_family: SPEC
atom_id: AN-S-2726
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T14:46:18.876464+00:00"
---

## Summary

Declare IS_BLOCKED_BY

## Claim

### Prose Claim

A dependent Plan may start only after each Plan it is blocked by is Done. BLOCKS is the inverse alias: the prerequisite is written before the dependent.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_BLOCKED_BY",
    inverse_alias="BLOCKS",
    endpoint_pairs=(
        {"source_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Plan)",)},
         "target_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Plan)",)}},
    ),
)
```

## Semantics

IS_BLOCKED_BY relates a dependent Plan to a prerequisite Plan.
