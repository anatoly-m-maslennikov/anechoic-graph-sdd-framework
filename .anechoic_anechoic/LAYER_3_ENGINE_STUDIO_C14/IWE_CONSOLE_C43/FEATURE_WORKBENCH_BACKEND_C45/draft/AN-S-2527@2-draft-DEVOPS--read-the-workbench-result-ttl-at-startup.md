---
identity:
  atom_id: AN-S-2527
context:
  container:
    component: C45
  tier: 5
  lens: DevOps
state:
  status: draft
  version: 2
  updated_at: '2026-11-14T00:32:36.680503+00:00'
---
## Summary

Read the Workbench result TTL at startup

## Claim

### Prose Claim

Read `workbench.result_ttl_seconds` at Workbench Backend startup from
`.anechoic_runtime/anechoic_runtime_settings.toml`.

## Details

- Use 3,600 seconds when the setting is absent.
- Reject an unreadable or invalid settings file.
- Reject a TTL that is not a positive integer.
