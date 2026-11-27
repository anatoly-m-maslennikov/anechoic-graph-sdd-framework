---
atom_family: SPEC
atom_id: AN-S-4741
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: DES
state:
  status: "active"
  version: 5
  updated_at: "2026-11-27T15:10:44.706424+00:00"

---

## Summary

Configure and emit Studio technical logs

## Claim

### Prose Claim

Use standard-library logging, the AN-S-1902 structured record and
severity rules, stderr, and bounded Docker retention. Keep diagnostics
separate from Flow, the Journal, and CLI or MCP results.

Runtime Setup owns `[logging]` in machine-wide `runtime.toml`. Default
to `INFO` and pass `ANECHOIC_LOG_LEVEL` once at startup. Direct and
development starts may set it explicitly. Accept only DEBUG, INFO,
WARNING, and ERROR.

Summarize routine file activity at INFO or bounded DEBUG. Corroborate
production evaluations with structured records or direct evidence.
Include UTC time, component, stable event code, operation, outcome,
level, and any run or correlation ID. Use monotonic step durations.
For failure or degradation, give scope and known action or retry
disposition.

Bound and sanitize evidence. Exclude raw arguments, bodies, SQL,
secrets, and unfiltered exception text. Minimize sensitive fields.
Pass structured context and emit the stack trace once at the handling
boundary. Logging failure preserves the primary outcome. Keep profiler
diagnostics in test images.
