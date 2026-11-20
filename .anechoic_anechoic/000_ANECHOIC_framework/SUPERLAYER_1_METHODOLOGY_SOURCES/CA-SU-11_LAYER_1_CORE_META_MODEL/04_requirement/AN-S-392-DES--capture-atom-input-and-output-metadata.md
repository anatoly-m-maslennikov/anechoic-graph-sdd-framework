---
identity:
  atom_id: AN-S-392
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
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
