---
atom_family: SPEC
atom_id: AN-S-1214
container:
  component: C34
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Control registered background services

# Control registered background services

`START_BACKGROUND_SERVICES` is an `ACTION_ENGINE` runtime-control operation. It **must** read one machine-readable registry from the selected installed release **and** expose status, pause, resume, stop, start, **and** reload for **every** enabled service.

**every** command **must** preserve accepted inbox, queue, action, receipt, circuit, **and** dead-letter state. pause stops new dispatch **without** deleting accepted intake. stop stops admission **and** reaches a declared safe shutdown boundary. start resumes admission **and** drains accepted work. reload reaches a safe boundary, re-resolves the selected installed release, restarts, **and** reconciles preserved work. No command **may** force termination across an unrecoverable mutation critical section.

the Tool **must** use dry-run **unless** apply is explicit, treat an empty registry as a successful no-op, reject duplicate **or** unsafe declarations **before** mutation, permit Framework implementation **only** from `.anechoic_runtime/tools`, write persistent operational state **only** below `.anechoic_runtime`, **and** write disposable process staging **and** cache state **only** below `.anechoic_tmp`. Repeated apply **must** be idempotent. Automatic restart **and** retry **must** remain within declared measured budgets. Exhausted budgets, governance failures, Journal failures, staging failures, ambiguous Git outcomes, **and** lease-integrity failures **must** open the circuit **or** pause autonomous dispatch **and** require explicit Operator recovery.
