---
atom_family: SPEC
atom_id: AN-S-4891
container:
  component: C31
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4890@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T11:30:15.361813+00:00'
---

## Summary

Group single actions by target

## Claim

### Prose Claim

Use the stable child Component ID for each family. This grouping leaves the operation, failure, and state rules to each family’s public Contract.

### Formal Claim

```python group
component_group(
    roles={'atom_actions': 'C35', 'scope_unit_actions': 'C36', 'projection_actions': 'C37', 'journal_actions': 'C38', 'project_actions': 'C39', 'queue_actions': 'C40'},
)
```
