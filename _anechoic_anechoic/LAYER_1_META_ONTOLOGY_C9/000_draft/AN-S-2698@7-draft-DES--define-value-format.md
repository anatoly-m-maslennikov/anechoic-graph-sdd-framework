---
atom_family: SPEC
atom_id: AN-S-2698
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T06:25:59.530754+00:00'
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
# model
composition(container='CFEL', parts=('Format',))
```

## Semantics

Format annotations constrain direct values. Markdown, YAML, TOML and JSON are
Carrier representation formats, not value Formats. The initial scalar
vocabulary—bool, datetime, decimal, float, int and string—is provisional. A
format annotation selects a value domain; it does not impose uniqueness.

