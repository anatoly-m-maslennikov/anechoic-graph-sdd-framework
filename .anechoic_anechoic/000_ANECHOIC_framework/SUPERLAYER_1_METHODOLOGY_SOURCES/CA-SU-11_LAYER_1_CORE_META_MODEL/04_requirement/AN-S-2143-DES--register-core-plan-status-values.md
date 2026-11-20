---
identity:
  atom_id: AN-S-2143
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: active
  version: 26
  updated_at: '2026-11-12T21:16:58.190634+00:00'
---
## Summary

Register Core Plan Status Values

## Claim

### Prose Claim


Core Plan Status values.


the Core Plan Status model **must** inherit the allowed values of Atom.Header.Status and add (Backlog, Done, Canceled). Planned **must not** be a distinct Plan Status.

### Formal Claim

```python
from anechoic.model import Plan
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Status",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.State",
    applies_to_entity_classes=(Plan,),
    allowed_values=("Backlog", "Done", "Canceled"),
    status_order_numbers={"Backlog": 1, "Done": 20, "Canceled": 40},
    status_groups={"Backlog": "Backlog"},
)
```
