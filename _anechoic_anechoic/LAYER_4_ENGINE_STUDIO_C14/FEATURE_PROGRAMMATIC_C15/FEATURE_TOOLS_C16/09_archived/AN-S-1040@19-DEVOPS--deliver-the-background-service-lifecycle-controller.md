---
atom_family: SPEC
atom_id: AN-S-1040
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Deliver the background-service lifecycle controller

# Deliver the background-service lifecycle controller

Realize START_BACKGROUND_SERVICES through 102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/START_BACKGROUND_SERVICES/start_background_services.py. Install the Tool **and** background_services.toml **in** the same selected release. Expose machine-readable describe, read-only status, **and** dry-run plus explicit apply forms of pause, resume, stop, start, **and** reload.

Give each service one .anechoic_runtime/services/<service-id> directory for process state, lifecycle state, logs, budgets, circuit state, **and** dead-letter references. Keep queue **and** action state **in** its declared Runtime state root so lifecycle commands never delete accepted work. Stop **and** reload use cooperative bounded shutdown **and** preserve an active mutation **until** a declared recoverable boundary. Platform-specific supervision remains behind a replaceable adapter.

the registry includes COMMIT_AUTOMATION **only** **when** its accepted Delivery **and** installed launcher exist. Status for that service reports selected release, process identity, admission, queue count **and** bytes, current action **and** phase, pending state, Git lease, last success **and** failure, budget usage, circuit state, **and** dead-letter count.
