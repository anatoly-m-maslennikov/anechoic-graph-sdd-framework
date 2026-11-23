---
atom_family: SPEC
atom_id: AN-S-295
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-25 06:44:11 +0400
---
## Summary

Keep triggered FPF work off the command-host path

# Keep triggered FPF work off the command-host path

**every** Hook-triggered **or** deferred FPF action **must** synchronously perform **only** bounded validation **and** durable idempotent intake **before** returning **to** the command host, **after** which the existing project-local asynchronous manager **and** Scheduler **must** dispatch isolated workers; the manager **must not** perform domain work **or** create one worker per Hook event, **and** the service **must** expose responsive manual `status`, `stop`, `start`, **and** `reload` controls plus bounded automatic timeout, heartbeat, retry, quarantine, restart, **and** circuit-breaker behavior while preserving accepted work **and** effect gates.
