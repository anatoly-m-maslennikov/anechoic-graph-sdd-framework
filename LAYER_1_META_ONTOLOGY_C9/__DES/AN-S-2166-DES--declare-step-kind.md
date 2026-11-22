---
atom_family: SPEC
atom_id: AN-S-2166
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T23:10:04.194712+00:00'
---

## Summary

Declare Step.Kind

## Claim

### Prose Claim

A Step has exactly one Kind: Input, Execution, or Decision. Kind classifies the Step in the Workflow and is independent of its Agentic Step Execution Context.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(entity_name='Kind', relation_name="IS_PROPERTY_OF", base_path='Atom/(.Header.Context.Role:=Operations)/Step', property_occurrence_cardinality=1, value_cardinality=1, allowed_values=("Input", "Execution", "Decision"))
```
