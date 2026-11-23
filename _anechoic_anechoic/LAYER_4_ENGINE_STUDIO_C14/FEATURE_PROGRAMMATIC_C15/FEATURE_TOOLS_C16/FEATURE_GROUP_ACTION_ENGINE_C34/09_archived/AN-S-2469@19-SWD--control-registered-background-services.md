---
atom_family: SPEC
atom_id: AN-S-2469
container:
  component: C34
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Control registered background services

# Summary

Control registered background services

## Scope

Queued background-service lifecycle action execution, process-state management, and governed operational sinks.

## Claim

Verify the selected runtime release, parse **and** validate its `background_services.toml`, expand **only** registered repository, runtime, temporary-state, Tool-root, **and** interpreter placeholders, **and** reject executable Framework Carriers outside `.anechoic_runtime/tools`.

For status, report admission, queue count **and** bytes, active action **and** phase, process identity, selected release, leases, last success **and** failure, budget usage, circuit state, **and** dead letters **without** mutation. For pause, stop new dispatch **and** preserve intake **and** action state. For resume **or** start, verify health **and** declared budgets, restore admission, **and** drain accepted work **without** starting a duplicate process. For stop, stop admission, request cooperative bounded shutdown, **and** wait for a declared recoverable boundary. For reload, stop at that boundary, re-resolve the selected release, restart, **and** reconcile preserved work.

Use atomic PID **and** lifecycle-state records below each Runtime service directory, with their atomic-write intermediates below `.anechoic_tmp`. Start processes **without** a shell, route technical and business log output to configured governed Journal sinks, which may be local or remote and need not use the runtime directory, route bytecode **and** disposable cache state **to** Project Temporary State, **and** verify the declared startup grace interval. Automatically restart **or** resume **only** a classified transient pre-mutation failure within its measured budget **and** **after** cooldown **and** health checks. Open the circuit **and** require explicit Operator recovery for exhausted budgets **or** governance, Journal, staging, ambiguous Git, **and** lease-integrity failures.

Stopping, reinstalling, reloading, or cleaning disposable service state must preserve accepted runtime Journal history and the Project Work Journal. A local sink is not disposable merely because a process wrote it; do not remove a runtime directory that contains retained Journal records.
