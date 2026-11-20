---
identity:
  atom_id: AN-S-2698
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-13T22:57:39.635646+00:00'
---
## Summary

Define Value Format

## Claim

### Prose Claim


Format defines the admissible value domain of each direct Property value,
separately from its cardinality. In CFEL, `Format` is the language element for
expressing that value domain. Data Type names the value domain. Uniqueness
Selection names the comparison population. List and map are Carrier
structures, not Value Formats. A YAML sequence carries multiple values, and a
mapping carries dependent Properties. `ref` is not a Value Format. Identifying
values use the `string` Format; their Definition identifies the referenced
object. Nested Properties have independent Formats and cardinalities. YAML
null and an empty string each count as one direct value when present; Format
and prose conditions determine admissibility.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity

class ValueFormat:
    pass

declare_entity(entity_name='Format', entity_class=ValueFormat)
```

## Semantics

Format annotations constrain direct values. Markdown, YAML, TOML and JSON are
Carrier representation formats, not value Formats. The initial scalar
vocabulary—bool, datetime, decimal, float, int and string—is provisional. A
format annotation selects a value domain; it does not impose uniqueness.
