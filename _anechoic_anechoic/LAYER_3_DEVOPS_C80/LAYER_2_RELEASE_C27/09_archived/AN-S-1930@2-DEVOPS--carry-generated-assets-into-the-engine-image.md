---
atom_family: SPEC
atom_id: AN-S-1930
container:
  component: C27
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: '2026-11-21T13:08:28.580728+00:00'
---
## Summary

Carry generated assets into the Engine image

## Claim

### Prose Claim

Include the MCP Tool Registry in the Engine image. Existing mode copies the checkout Registry. Local Release refresh generates and verifies it before recording it at the Git checkpoint.

Compile the native Model at Project startup. Workbench derives its schema and relation metadata from the native runtime.