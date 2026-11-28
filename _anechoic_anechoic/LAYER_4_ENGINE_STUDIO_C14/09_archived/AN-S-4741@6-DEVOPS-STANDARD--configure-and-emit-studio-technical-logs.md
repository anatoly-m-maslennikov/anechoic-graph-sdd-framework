---
atom_family: SPEC
atom_id: AN-S-4741
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: DevOps
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-27T20:35:14.221449+00:00"

---

## Summary

Configure and emit Studio technical logs

## Claim

### Prose Claim

Send the technical log records defined in AN-S-5187 to stderr. Bound Docker log retention. Keep diagnostics
separate from Flow, the Journal, and CLI or MCP results.

Runtime Setup owns `[logging]` in machine-wide `runtime.toml`. Default
to `INFO` and pass `ANECHOIC_LOG_LEVEL` once at startup. Direct and
development starts may set it explicitly. Accept only DEBUG, INFO,
WARNING, and ERROR.

Corroborate production evaluations with structured records or direct
evidence. Keep profiler diagnostics in test images.
