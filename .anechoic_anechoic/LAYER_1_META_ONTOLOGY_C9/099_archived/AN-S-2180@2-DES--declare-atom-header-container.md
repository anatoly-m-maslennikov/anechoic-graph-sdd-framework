---
identity:
  atom_id: AN-S-2180
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-13T00:55:28.879761+00:00'
---
## Summary

Declare Atom.Header.Container

## Claim

### Prose Claim

Header.Container identifies the Atom's immediate Container.

Header.Container contains exactly one key: `atom` names the containing Atom by its base Atom ID, or `scope_unit` names the containing Scope Unit by its stable ID. A base Atom ID selects Current by default.

For a root Project Declaration Atom, an omitted Header.Container has the effective default mapping with `scope_unit` equal to `CA-SU--1`, identifying the predefined Scope Unit `world`. An explicit valid value overrides that default.
Header.Container is the sole stored Atom-containment value.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Container",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=1,
    allowed_dependent_property_names=("atom", "scope_unit"),
)
```
