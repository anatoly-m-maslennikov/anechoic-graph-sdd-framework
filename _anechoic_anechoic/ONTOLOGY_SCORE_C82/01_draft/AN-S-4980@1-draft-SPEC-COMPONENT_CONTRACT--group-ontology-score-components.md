---
atom_family: SPEC
atom_id: AN-S-4980
container:
  component: C82
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-4909
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:41:51.963778+00:00'
---

## Summary

Group the Ontology Score Components.

## Guarantee

Group Continuant Pitchfork and Occurrent Metronome under Ontology Score. Their published Manifests declare their respective identities and containment.

## Claim

### Formal Claim

```python group
declare_group_contract(
    roles={'continuant_pitchfork': 'C9', 'occurrent_metronome': 'C58'},
    entry_points=[],
)
```
