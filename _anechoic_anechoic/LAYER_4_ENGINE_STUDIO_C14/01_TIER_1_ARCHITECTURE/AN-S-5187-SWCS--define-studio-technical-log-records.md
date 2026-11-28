---
atom_family: SPEC
atom_id: AN-S-5187
container:
  component: C14
tier: 1
context:
  lens: SWD/SWCS
state:
  status: active
  version: 1
  updated_at: "2026-11-27T18:10:33.685998+00:00"
---

## Summary

Define Studio technical log records

## Claim

Use the Python standard-library logging API. Follow the structured record
and severity rules in AN-S-1902.

Summarize routine file activity at INFO or bounded DEBUG.
Include UTC time, component, stable event code, operation, outcome,
level, and any run or correlation ID. Use monotonic step durations.
For failure or degradation, give scope and known action or retry
disposition.

Bound and sanitize evidence. Exclude raw arguments, bodies, SQL,
secrets, and unfiltered exception text. Minimize sensitive fields.
Pass structured context and emit the stack trace once at the handling
boundary. Logging failure preserves the primary outcome.
