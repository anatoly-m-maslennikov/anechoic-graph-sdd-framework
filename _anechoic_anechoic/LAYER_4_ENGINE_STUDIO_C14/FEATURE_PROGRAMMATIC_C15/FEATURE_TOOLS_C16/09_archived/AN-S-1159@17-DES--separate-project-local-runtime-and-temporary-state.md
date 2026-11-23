---
atom_family: SPEC
atom_id: AN-S-1159
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 17
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Separate project-local runtime and temporary state

# Separate project-local runtime and temporary state

**all** Tools **in** one ANECHOIC Project **must** use one project-local runtime rooted
at `.anechoic_runtime/` **and** one project-local temporary-state root at
`.anechoic_tmp/`. the runtime **contains** content-addressed executable releases,
shared non-executable libraries, machine-readable registries, declared
dependencies, stable launchers, Hook Carriers, logs, sessions, databases,
service state, **and** resumable state. the temporary-state root **contains** **only**
disposable scratch, staging, cache, build, Evaluation, atomic-write
intermediate, **and** interrupted-cleanup Carriers.

an installed Tool **must** import executable **and** non-executable implementation
**only** from its selected release under `.anechoic_runtime/tools/`; it **must not**
import Framework implementation from the canonical source tree, the configured
Project control root, `.anechoic_tmp/`, **or** another Project path. host
interpreters **and** Git remain declared substrate dependencies rather than copied
Framework implementation. a host-required discovery Carrier **may** point into
`.anechoic_runtime/tools/`, but it **must** contain no independent Framework
behavior **and** **must not** become dependency authority.
