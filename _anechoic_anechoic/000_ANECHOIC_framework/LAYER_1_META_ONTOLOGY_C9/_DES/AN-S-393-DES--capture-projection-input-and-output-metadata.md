---
atom_family: SPEC
atom_id: AN-S-393
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Capture Projection input and output metadata

## Claim

### Prose Claim


An Event Record for Projection creation or update has object_output. An update record also has object_input; creation input is optional.

For each present Projection input or output, the Event Record captures:

- Projection.ID.
- Projection.Updated At.

object_input contains the values before the change. object_output contains the values after it. Neither side contains a Version. The captured values remain as recorded.
