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
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:04:00.940384+00:00"

---

## Summary

Configure and emit Studio technical logs

## Claim

### Prose Claim

Use Python standard-library logging and the structured record schema
of AN-S-1902. Write technical records to stderr. Preserve the existing
bounded Docker logging and retention. Keep technical diagnostics
separate from Flow, Journal, and CLI or MCP result contracts.

Runtime Setup owns one machine-wide `[logging]` table in `runtime.toml`.
Use `level = "INFO"` when no level is set. At startup, pass the selected
level to Studio processes once through `ANECHOIC_LOG_LEVEL`. Direct
and development starts can set that environment variable explicitly.

Accept exactly `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Reject other values.
Apply the operational classification in AN-S-1902.

- ERROR reports a failure that can affect correctness or availability, or needs retry or intervention.
- WARNING reports unexpected or degraded behavior that recovered, used a fallback, or remains within an accepted tolerance.
- INFO reports material lifecycle, business, and operational milestones or summarized progress.
- DEBUG reports bounded, sanitized internal state or decision details for diagnosis.

Omit routine records for individual files. Corroborate free-form log prose
with structured records or direct evidence before making a production evaluation.

Give each record a UTC timestamp, level, component, stable event code,
operation, and outcome. Include the existing run or correlation ID when
available. Measure step duration with a monotonic clock.

Record only bounded, sanitized evidence. Exclude raw arguments, bodies,
SQL, secrets, and unfiltered exception text. Logging failure must not
change the primary operation's outcome. Keep profiler diagnostics in
test images.
