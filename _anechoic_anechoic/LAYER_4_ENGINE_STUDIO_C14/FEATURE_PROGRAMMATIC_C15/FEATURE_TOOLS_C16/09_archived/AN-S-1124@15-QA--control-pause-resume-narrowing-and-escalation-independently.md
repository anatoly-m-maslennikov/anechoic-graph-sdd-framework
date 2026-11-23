---
atom_family: SPEC
atom_id: AN-S-1124
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Control pause, resume, narrowing, and escalation independently

# Control pause, resume, narrowing, and escalation independently

## Test case

pause **and** narrow an active envelope while work is queued, **then** attempt resume, replacement, **and** expansion from the executor, the original authorizer, **and** the registered independent override authority. repeat **after** an integrity-sensitive failure.

## Acceptance criteria

pause **and** narrowing take effect **before** the next dispatch **or** commit. the executor cannot resume, replace, expand, **or** self-authorize. **only** the registered independent authority **may** resume under the same bounds **or** issue a replacement; expansion **and** integrity recovery require a new explicitly authorized envelope.
