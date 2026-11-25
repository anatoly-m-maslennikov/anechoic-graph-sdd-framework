---
atom_family: SPEC
atom_id: AN-S-3304
container:
  component: C16
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3056
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:00:30.733108+00:00'
---

## Summary

Apply one admitted native lifecycle operation

## Guarantee

For the selected Project, dispatch one supported Atom lifecycle operation
against the admitted carrier capture. For a change to an existing Atom,
require its exact expected revision. Reject an invalid or stale target
before writing.

## Claim

### Prose Claim

The output record properties identify logical fields. A preflight
rejection reports invalid or stale input before lifecycle dispatch.

### Formal Claim

```python cli
declare_cli_contract(
    interface='task_lifecycle',
    action='apply_native_lifecycle',
    runner='managed_python',
    module='FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli',
    stdin=('bound Task, Epic, or Ticket Asset lifecycle request and '
           'Model and Structure attestation on stdin'),
    stdout={'succeeded': 'native outcome and file effects on stdout'},
    output='preflight_rejected',
    forbid_effect=('lifecycle_dispatch', 'atom_write'),
    checks={'output_format': {'record_properties': ('outcome', 'file_effects')}},
)
```
