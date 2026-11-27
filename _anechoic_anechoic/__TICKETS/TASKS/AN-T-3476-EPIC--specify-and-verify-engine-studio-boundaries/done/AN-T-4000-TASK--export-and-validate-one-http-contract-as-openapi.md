---
atom_family: TKT
atom_id: AN-T-4000
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:37:48.873826+00:00"
---
## Summary

Export and validate one HTTP Contract as OpenAPI

## Acceptance

Choose one named POST /tools Action in an isolated provider fixture. Author explicit request and named response schemas, including presence, nullability and extra-field behavior. Reuse jsonschema for payloads. Generate and validate the OpenAPI document from the pinned Manifest as the authored source.
