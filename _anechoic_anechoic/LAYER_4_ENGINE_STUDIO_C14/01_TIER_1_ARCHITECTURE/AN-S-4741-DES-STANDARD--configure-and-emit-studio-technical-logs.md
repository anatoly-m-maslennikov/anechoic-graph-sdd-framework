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
  version: 4
  updated_at: "2026-11-25T22:40:45.665582+00:00"

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

Omit routine records for individual files. Summarize repeated normal activity at INFO or use bounded DEBUG. Corroborate free-form log prose
with structured records or direct evidence before making a production evaluation.

Give each record a UTC timestamp, level, component, stable event code,
operation, and outcome. Include the existing run or correlation ID when
available. Measure step duration with a monotonic clock. For a failure or degradation, identify the affected scope and any known operator action or retry disposition.

Record only bounded, sanitized evidence. Exclude raw arguments, bodies,
SQL, secrets, and unfiltered exception text. Minimize personal, customer,
and commercially sensitive data under its applicable boundary. Emit an
exception at the boundary that handles or escalates it. Pass structured
context across lower boundaries and emit the stack trace once.

Logging failure must not
change the primary operation's outcome. Keep profiler diagnostics in
test images.
