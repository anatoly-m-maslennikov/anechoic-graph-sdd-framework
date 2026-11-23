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
  version: 1
  updated_at: 2026-10-27 21:53:07 +0400
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

## Draft

CA-R-2194's next-version Draft states this boundary and keeps the distinction between the Runtime context, work executed there and records describing it. Current sources and the Projection remain unchanged until promotion.
