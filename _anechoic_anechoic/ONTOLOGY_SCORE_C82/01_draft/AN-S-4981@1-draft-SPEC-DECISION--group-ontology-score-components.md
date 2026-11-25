---
atom_family: SPEC
atom_id: AN-S-4981
container:
  component: C82
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-4980@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:41:51.963778+00:00'
---

## Summary

Group the Ontology Score Components.

## Claim

### Prose Claim

Use the published Component IDs to group the two children. Each child
owns its internal content.

### Formal Claim

```python group
component_group(
    roles={'continuant_pitchfork': 'C9', 'occurrent_metronome': 'C58'},
    entry_points=[],
)
```
