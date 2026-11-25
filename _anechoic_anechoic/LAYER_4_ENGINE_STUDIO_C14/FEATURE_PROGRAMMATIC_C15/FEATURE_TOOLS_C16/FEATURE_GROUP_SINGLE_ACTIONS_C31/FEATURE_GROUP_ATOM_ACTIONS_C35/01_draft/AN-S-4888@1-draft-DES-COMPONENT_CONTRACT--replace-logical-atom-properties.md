---
atom_family: SPEC
atom_id: AN-S-4888
container:
  component: C35
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3076
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Replace logical Atom Properties.

## Guarantee

Admission requires exactly one explicit Atom target before Find. Reject zero, multiple or implicit targets before selection or change.

Find and replace uses one explicit Atom target and admitted logical Atom Properties or content sections, not unrestricted file text. Find, Check and Change remain separate Single Actions. Find returns the selected Atom identity and current values within the explicit Scope and lifecycle frontier.

Each Update receives the exact Atom identity, expected current state, logical Property or section, full old value and full computed new value. Literal text replacement uses a nonempty search text and replaces all occurrences in the selected value. Unselected content remains unchanged.

Summary and Type changes use the existing fresh-ID replacement path.
For multiple targets, the C18 Workflow owns sequencing and the
disposition of completed and remaining Actions.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='replace_logical_atom_properties',
    output='change_reported',
    must_effect=(('logical_target', 'one_explicit'), ('logical_target', 'selected'), ('expected_state', 'checked'), ('change', 'completed')),
    must_precede=((('logical_target', 'one_explicit'), ('logical_target', 'selected')),
                  (('logical_target', 'selected'), ('expected_state', 'checked')),
                  (('expected_state', 'checked'), ('change', 'completed'))),
)
```

```python trace
declare_trace_contract(
    action='replace_logical_atom_properties',
    output='invalid_target_rejected',
    must_effect=(('logical_target', 'invalid_cardinality'),),
    forbid_effect=('change',),
)
```
