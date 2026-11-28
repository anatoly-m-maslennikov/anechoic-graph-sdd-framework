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
  status: "active"
  version: 7
  updated_at: "2026-11-27T20:35:14.221449+00:00"

---

## Summary

Configure and emit Studio technical logs

## Claim

### Prose Claim

Apply AN-S-5187 to Studio technical log records. Send DEBUG and INFO to
stdout, and WARNING and ERROR to stderr. If stdout carries protocol or
result data, send all diagnostics to stderr. Keep technical diagnostics
separate from Flow and the business Journal.

Use Docker's local logging driver with `max-size=10m`, `max-file=3`,
`mode=non-blocking`, and `max-buffer-size=1m`. A full buffer may drop new
messages. The logs expire with the container. Use no separate local log
directory.

Runtime Setup owns `[logging]` in machine-wide `runtime.toml`. Default
to `INFO` and pass `ANECHOIC_LOG_LEVEL` once at startup. Direct and
development starts may set it explicitly. Accept only DEBUG, INFO,
WARNING, and ERROR.

Corroborate production evaluations with structured records or direct
evidence. Keep profiler diagnostics in test images.
