---
atom_family: SPEC
atom_id: AN-S-4890
container:
  component: C31
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3071
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T11:30:15.361813+00:00'
---

## Summary

Group single actions by target

## Guarantee

Group the six declared Action families by their target. An Atom Action takes one explicit Atom target. The owning Workflow sequences separate Actions when it accepts several targets.

## Claim

### Formal Claim

```python group
declare_group_contract(
    roles={'atom_actions': 'C35', 'scope_unit_actions': 'C36', 'projection_actions': 'C37', 'journal_actions': 'C38', 'project_actions': 'C39', 'queue_actions': 'C40'},
)
```
