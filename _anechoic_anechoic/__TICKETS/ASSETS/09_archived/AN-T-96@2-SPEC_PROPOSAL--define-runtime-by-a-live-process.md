---
atom_family: TKT
atom_id: AN-T-96
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-27 22:47:33 +0400
---
## Summary

Define Runtime by a live process

# Summary

Define Runtime by a live process

## Question

Does a Runtime continue to exist while it is idle?

## Operator decision

“if some process is alive, yes. if no, then no. we have docker container running”

A Runtime exists while its process is alive. Being idle or waiting for work does not end that Runtime. When its process is no longer alive, the Runtime no longer exists. A running Docker container is the concrete example.

## Scope

This resolves C10-I06 / C10-G04 by clarifying the existing Runtime definition. It does not add a lifecycle entity, mandatory process field, readiness test, health check or runtime implementation change.

## Adoption result

Current R2194@3 defines Runtime by a live process, including idle time, and retains the running Docker container example. Its predecessor is archived.

[Rebuilt main Subject view](../_projection/CA-PROJ-009-ANECHOIC--Subject-Graph--Current-RMEDO.md).
