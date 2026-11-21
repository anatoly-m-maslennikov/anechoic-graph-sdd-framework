---
atom_family: SPEC
atom_id: AN-S-3191
container:
  component: C21
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-21T17:36:24.701358+00:00'
---

## Summary

Delegate admitted MCP Tool calls

## Guarantee

For the selected Project, admit exposed Tool requests against the active
registry and the Tool's input schema. Delegate each admitted request to the
canonical provider registered for the Tool. Transport the validated result
or a failure through MCP.

Reject a request before dispatch when the Tool is unavailable for the Project
or the input fails validation.

## References

AN-S-1381, AN-S-3044, and AN-T-2947.
