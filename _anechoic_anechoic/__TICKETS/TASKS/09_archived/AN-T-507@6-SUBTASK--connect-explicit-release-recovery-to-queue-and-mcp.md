---
atom_family: TKT
atom_id: AN-T-507
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 13:51:47 +0400
---
## Summary

Connect explicit Release recovery to queue and MCP

# Summary

Connect explicit Release recovery to queue and MCP

## Objective

Deliver the typed public and durable-queue path to the existing frozen Release recovery implementation.

## Details

1. review CA-R-1883, CA-M-340, CA-E-583 and CA-D-577 before implementation.
2. admit only the existing frozen Release Run through the closed recovery request. Ordinary enqueue and redispatch never become recovery.
3. preserve the canonical Run identity and exact sealed request, source, approval, permission, checkpoint and Journal bindings. Scheduler transport identity is not a second canonical Run.
4. recover exact pending recording through the shared writer; leave uncertain/in-progress effects blocked and never replay them.
5. test request rejection before queue admission, source/permission staleness, exact worker delegation and truthful observation without inventing starts or terminal evidence.
6. the bounded implementation/review estimate is <=15 minutes; decompose further if actual remaining work exceeds that bound.

## Definition of Done

Reviewed source, strict CLI/MCP/queue boundaries and focused tests connect an explicit admitted recovery request to the existing private recovery method. Normal selected execution remains unchanged. Live queue/MCP recovery and canonical Journal proof are required separately before full Release closure.
