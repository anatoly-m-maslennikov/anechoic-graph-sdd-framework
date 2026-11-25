---
atom_family: TKT
atom_id: AN-T-3957
concern:
- subject: C75
  path: Project Structure.components
  relation: affects
container:
  component: C75
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C75 drops source context on malformed input

## Claim

### Prose Claim

The missing-link and malformed-header paths return a string. They omit the source pin and field that C90's diagnostic can preserve.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/formal_chain__pub.py:31.

## Resolution criteria

Return a structured diagnostic with the relevant source pin and field where available.

## Resolution

Malformed headers and missing links now return diagnostics with the source pin, field, and role.
