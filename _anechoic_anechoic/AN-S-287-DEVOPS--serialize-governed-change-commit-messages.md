---
atom_family: SPEC
atom_id: AN-S-287
container:
  component: C00
tier: 1
context:
  lens: DevOps
state:
  status: active
  version: 21
  updated_at: 2026-10-27 19:59:23 +0400
---
## Summary

Serialize Governed Change Commit Messages

# Serialize Governed Change Commit Messages

**every** Git Commit message created by a ANECHOIC Tool **must** be the deterministic one-line Projection of exactly one sealed Git-effect action: a real-change action uses `<initiative-summary> | <CHANGE_CLASS> | <affected-subject>`, **where** the Initiative summary is derived from the governing human Plan, Task, **or** ephemeral session task; a Journal-only batch uses `JOURNAL BATCH | APPEND | <journal-batch-id>`. A real-change message **must not** use a technical parent **in** place of the Initiative summary, **and** neither message class **may** impersonate **or** be combined with the other.
