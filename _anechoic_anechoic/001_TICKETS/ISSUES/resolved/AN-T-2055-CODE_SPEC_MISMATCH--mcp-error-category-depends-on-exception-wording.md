---
atom_family: TKT
atom_id: AN-T-2055
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-20T20:35:37.542498+00:00'
---
## Summary

MCP error category depends on exception wording

## Claim

### Prose Claim

CA-M-396@17 prohibits classifying failure by arbitrary human-message substrings. `FEATURE_MCP/shared_gateway.py` maps a HostRuntimeConfigError to an outside-project category when its text contains `outside`. The same exception type carries prose from `FEATURE_TOOLS/host_runtime_config.py`. Wording changes can alter the machine-readable error category.
