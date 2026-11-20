---
atom_family: SPEC
atom_id: AN-S-464
structure:
  container:
    component: C9
  tier: 6
context:
  lens: DevOps
state:
  status: active
  version: 27
  updated_at: 2026-11-04 09:30:21 +0400
---
## Summary

Serialize the framework control-root locator

## Claim

### Prose Claim


an explicitly selected framework control-root locator in the Project's Framework Settings TOML Carrier.


when the framework control-root locator is explicitly selected, the Framework Settings TOML Carrier **must** encode it and it **must** resolve **to** the Directory Carrier prescribed by CA-D-317 **without** selecting a different authority root.
