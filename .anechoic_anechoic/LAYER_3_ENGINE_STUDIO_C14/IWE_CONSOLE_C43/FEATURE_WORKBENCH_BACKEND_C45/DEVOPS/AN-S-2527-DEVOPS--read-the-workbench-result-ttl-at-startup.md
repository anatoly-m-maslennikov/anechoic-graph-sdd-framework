---
identity:
  atom_id: AN-S-2527
context:
  container:
    component: C45
  tier: 5
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:27:51.761044+00:00'
---
## Summary

Read the Workbench result TTL at startup

## Claim scope

Workbench Backend startup configuration.

## Claim

### Prose Claim

Read `workbench.result_ttl_seconds` from `.anechoic_runtime/anechoic_runtime_settings.toml` at startup. Use 3,600 seconds if the setting is absent. Reject an unreadable or invalid settings file and a TTL that is not a positive integer.
