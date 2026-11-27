---
atom_family: SPEC
atom_id: AN-S-392
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T09:25:56.658653+00:00"
---
## Summary

Capture Atom input and output metadata

## Claim

### Prose Claim


An Event Record for Atom creation or update has object_output. An update record also has object_input; creation input is optional.

For each present Atom input or output, the Event Record captures:

- Atom.Header.ID.
- Atom.Header.Version.
- Atom.Header.Updated At.

object_input contains the values before the change. object_output contains the values after it. Their IDs may differ. The captured values remain as recorded.
