---
atom_family: SPEC
atom_id: AN-S-4972
container:
  component: C72
tier: 0
context:
  template: component_contract
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-3342
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:41:25.002107+00:00'
---

## Summary

Provide Project environments

## Guarantee

Engine Studio, Release, and Setup have separate uv Projects. Each has its own Python import root and `pyproject.toml` and `uv.lock` under the respective `engine/`, `release/`, or `setup/` directory in C72. AN-S-3310@10 defines their use and isolation.

## Claim

### Prose Claim

This conceptual handoff records the three environment artifacts as available. It does not create, install, or verify the environments.

### Formal Claim

```python trace
declare_trace_contract(
    action='provide_project_environments',
    output='environments_available',
    must_effect=(('engine_environment', 'available'), ('release_environment', 'available'), ('setup_environment', 'available')),
)
```
