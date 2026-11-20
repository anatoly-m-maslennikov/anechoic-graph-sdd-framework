---
identity:
  atom_id: AN-S-1245
context:
  container:
    component: C15
  tier: 1
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Confine all temporary state to project temp

## Claim

### Prose Claim

**every** temporary File **or** Directory Carrier created by a ANECHOIC-controlled
PROGRAMMATIC execution **must** be located below the configured Project
Temporary State root `.anechoic_tmp/`. This obligation applies **to** Tools, App backend
services, MCP components, their tests **and** Evaluations, their launchers, **and**
dependencies whose execution they configure. It includes temporary, scratch,
staging, cache, intermediate build **or** Evaluation, **and** interrupted-cleanup
Carriers.
Python bytecode caches, including **every** `__pycache__/` Directory Carrier **and**
`.pyc` File Carrier, are temporary cache state under this obligation.

A PROGRAMMATIC component **must not** use the repository root, the process
working directory, a source **or** Delivery Carrier, the Project control root,
`.anechoic_runtime/`, **or** a host temporary root as a fallback. If the Project
Temporary State root is unavailable, an invoked dependency cannot be redirected,
**or** a required same-filesystem atomicity precondition cannot be satisfied, the
component **must** stop **before** the affected effect **and** report the boundary
failure with one stable diagnostic identifying its creating owner **and**
violating path.

retained temporary paths **must** preserve their owner **and** run identity.
temporary confinement **must** remain correct **when** bounded cleanup is interrupted
**or** denied; cleanup completion is **not** a prerequisite for confinement.

Temporary state **must not** become authority **or** installed implementation.
Deleting `.anechoic_tmp/` **may** discard caches, diagnostics, disposable
workspaces, **or** interrupted-cleanup remnants, but **must not** discard a governed
Artifact, Project Journal history, an installed release, **or** resumable runtime
progress.

