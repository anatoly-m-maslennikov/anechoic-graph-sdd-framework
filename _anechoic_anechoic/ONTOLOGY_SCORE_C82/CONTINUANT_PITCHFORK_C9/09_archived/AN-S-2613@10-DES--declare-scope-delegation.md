---
atom_family: SPEC
atom_id: AN-S-2613
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 10
  updated_at: '2026-11-11T16:37:55+04:00'
---
## Summary

Declare Scope Delegation

## Claim

### Prose Claim

Scope Delegation is one generic Form for an external Atom whose Role is in RMEDO. Its active Subject identifies exactly one receiving non-Project Scope Unit within the Project. Its Container is that unit’s direct structural Parent. The Parent assigns a contribution to the receiving unit and retains its broader scope and accountability.

A Scope Delegation states the receiving Scope Unit's responsibilities and admits Main Subject selections in its Prose Claim. The Scope Unit Declaration states the receiving unit's structural facts in its Formal Claim.

For local admission, the Atom's Container resolves to the receiving Scope Unit. Its Main Subject resolves to an endpoint admitted by at least one applicable Scope Delegation. The Model determines valid Role and Form combinations.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Form', relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context', allowed_values=('Scope Delegation',),
    form_roles=('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'),
)
```
