---
atom_family: SPEC
atom_id: AN-S-4010
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-29 10:17:25 +0400
---
## Summary

Define Runtime

## Claim

Runtime **means** a live technical execution context for Implementation. a Runtime exists while its process is alive, including when that process is idle or waiting for work. when the process is no longer alive, that Runtime no longer exists.

### Formal claim

```text
Runtime ((EXECUTES)) Workflow Run
```

## Semantics

A running Docker container is an example of a Runtime. A Runtime can remain alive while no Workflow, Step or Action is executing. An Execution is the work performed within the context. Stored descriptions and Journal records are not the Runtime itself.
