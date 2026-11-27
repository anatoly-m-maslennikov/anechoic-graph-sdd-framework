---
atom_family: SPEC
atom_id: AN-S-5058
container:
  component: C31
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3071@4-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Group single actions by target.

## Claim

### Prose Claim

The children own their operation, failure and state rules. Each Atom mutation takes one explicit target. Read-only Find searches the explicit frontier under AN-S-2397@5. C18 sequences separate mutations under AN-S-2422@12.

### Formal Claim

```python group
component_group(
    roles={'atom_actions': 'C35', 'scope_unit_actions': 'C36', 'projection_actions': 'C37', 'journal_actions': 'C38', 'project_actions': 'C39', 'queue_actions': 'C40'},
    entry_points=(),
)
```
