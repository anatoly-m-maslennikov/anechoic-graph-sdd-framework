---
atom_family: SPEC
atom_id: AN-S-1512
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify logging lifecycle materialization

## Claim

### Prose Claim

Reject deployment until a production-relevant component materializes active Logging Policy sink, retention, access, sampling, rotation, size, back-pressure, unavailable-sink and disk-pressure boundaries; implementation/delivery do not claim policy authority. For the selected Docker runtime, verify structured technical diagnostics go to stderr, local rotation uses `max-size=10m` and `max-file=3`, and non-blocking mode uses `max-buffer-size=1m`; when the buffer is full, new technical messages may be dropped without stalling primary work.
