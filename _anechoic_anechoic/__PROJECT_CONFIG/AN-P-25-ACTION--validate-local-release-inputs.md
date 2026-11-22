---
atom_family: PROJECT_CONFIG
atom_id: AN-P-25
structure:
  container:
    component: C27
context:
  template: action
state:
  status: active
  version: 24
  updated_at: '2026-11-21T21:51:04.697298+00:00'
---

# Summary

Validate local release inputs

## Action

Validate the selected Project, required checked-in assets, and configured delivery paths for ordinary input and file/path safety. Missing, ambiguous or unsafe input stops before tests or delivery writes. This Action does not invoke a compiler or ANECHOIC runtime Component.
