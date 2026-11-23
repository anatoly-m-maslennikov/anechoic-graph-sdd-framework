---
atom_family: SPEC
atom_id: AN-S-1111
container:
  component: C34
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 03:32:22 +0400
---
## Summary

Complete one installed automatic commit end to end

# Complete one installed automatic commit end to end

## Claim checked

the exact installed release completes one automatic provenance action **without** blocking Codex command dispatch.

## Test case

install **and** activate a fresh release, start COMMIT_AUTOMATION, invoke one Codex Tool that changes one admitted subject, **and** observe Hook latency, inbox acceptance, persisted phases, Journal evidence, Git evidence, status, **and** restart recovery.

## Acceptance criteria

the Codex Tool result is **not** delayed by provenance completion; one event is durably accepted; the service executes **only** the fixed pipeline; the independent Journal **and** real-change Git outcomes match the sealed action; status is complete **and** read-only; **and** restart produces no duplicate effect.

## Failure disposition

reject release readiness **if** static validation, installation status, **or** dry-run is the **only** evidence, **or** **if** the fresh installed operation blocks, loses, duplicates, misattributes, **or** cannot recover the action.
