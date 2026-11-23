---
atom_family: SPEC
atom_id: AN-S-2470
container:
  component: C34
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Start each enabled service once

# Summary

Start each enabled service once

## Scope

Evaluation of one background-service lifecycle action and its recorded outcome.

## Claim

## Claim checked

Apply starts each enabled installed service once **and** repeated apply recognizes its live process.

## Test case

Install one enabled long-running Python service, invoke dry-run, apply, apply again, **and** status.

## Acceptance criteria

Dry-run predicts one start **without** mutation. First apply starts one process **and** writes its disposable PID state only under its runtime service directory and appends technical and business log Journal records to their explicitly configured governed local or remote sinks. Second apply reports the same PID as already running **and** starts no process. Status reports one enabled **and** running service; `.anechoic_runtime/tools` **contains** no Python cache; **and** disposable bytecode **and** cache Carriers exist **only** below `.anechoic_tmp`.

## Failure disposition

Reject delivery **if** dry-run mutates, apply duplicates a live service, disposable process state is written outside `.anechoic_runtime`, configured log Journal sinks are bypassed, or stopping or cleaning disposable state changes accepted runtime Journal history, implementation is read outside `.anechoic_runtime/tools`, **or** liveness is reported incorrectly.
