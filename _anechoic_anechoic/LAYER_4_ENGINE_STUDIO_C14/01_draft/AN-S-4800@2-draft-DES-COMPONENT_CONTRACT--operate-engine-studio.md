---
atom_family: SPEC
atom_id: AN-S-4800
container:
  component: C14
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3039
state:
  status: "draft"
  version: 2
  updated_at: "2026-11-25T10:44:09.747098+00:00"
---
## Summary

Operate Engine Studio

## Guarantee

Provide the Studio runtime by delegating its interfaces, Project state,
and execution to its child Components. The supervised runtime
coordinates their lifecycle.

## Claim

### Prose Claim

Kernel and Orchestrator identify the two roles in the selected Project's
runtime pair. Each readiness signal applies to that pair. Report readiness
only after validating the Project Manifest binding, confirming both roles
are ready, and confirming Current and Draft catch-up. Report an invalid
Manifest for the affected Project and block its writes.

### Formal Claim

```python trace
declare_trace_contract(
    action='admit_studio_readiness',
    output='ready',
    must_effect=(('project_manifest', 'binding_validated'), ('kernel', 'ready'),
                 ('orchestrator', 'ready'), ('current_and_draft', 'catch_up_confirmed')),
    forbid_effect=('invalid_manifest',),
)
```

```python trace
declare_trace_contract(
    action='admit_studio_readiness',
    output='manifest_invalid',
    must_effect=(('invalid_manifest', 'reported'),),
    forbid_effect=('affected_project_write',),
)
```
