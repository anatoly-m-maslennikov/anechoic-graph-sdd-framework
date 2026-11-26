---
atom_family: SPEC
atom_id: AN-S-3311
container:
  component: C52
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3066
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:53:53.766836+00:00'
---
## Summary

Supply the bundled Model classes

## Guarantee

Provide the bundled Python Model classes to admitted consumers. An Atom
has separate Header and Content fields with the bundled field contracts.
Plan is an Atom subtype and uses the same fields.

## Claim

### Prose Claim

Header and Content stand for the bundled field types. The model leaves their
internal field contracts abstract.

### Formal Claim

```python shape
declare_shape_contract(
    record='Atom',
    fields={'header': 'Header', 'content': 'Content'},
    subtype='Plan',
)
```
