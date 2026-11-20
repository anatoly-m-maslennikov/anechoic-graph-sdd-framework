---
identity:
  atom_id: AN-T-2055
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:45.141616+00:00'
---
## Summary

MCP error category depends on exception wording

## Claim

### Prose Claim

CA-M-396@17 prohibits classifying failure by arbitrary human-message substrings. `FEATURE_MCP/shared_gateway.py` maps a HostRuntimeConfigError to an outside-project category when its text contains `outside`. The same exception type carries prose from `FEATURE_TOOLS/host_runtime_config.py`. Wording changes can alter the machine-readable error category.
