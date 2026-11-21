---
atom_family: TKT
atom_id: AN-T-1478
structure:
  container:
    atom: AN-T-1482
  priority: 2
context:
  template: task
state:
  status: "canceled"
  version: 1
  updated_at: "2026-11-20T20:06:18.293724+00:00"
---
## Summary

Reconcile deferred Engine Scope Goals

## Objective

Resolve four legacy Engine Goals against the Engine Subject and Scope Unit revision, preserving their useful meaning before any change.

## Details

P2701 deliberately leaves CA-R-1186, CA-R-1601, CA-R-1602 and CA-R-1606 unchanged. R1186 names old TOOLS groups CONNECTORS/ANECHOIC_TOOLS. The other three refer to ACTION_PROMPTS, OPERATOR_PROMPTS and AGENT_HOST_PLUGINS, which are not registered Scope Units. Decide whether these are still-needed boundaries, ordinary engineering requirements/decisions, renamed existing groups or obsolete content; do not invent units or targets. Current Claims and identities remain authoritative until that review. This is part of the existing Engine methodology migration, not implementation. GIT/FPF Goals R1469/R1474/R1482 remain separately deferred by the Operator and are not reactivated here.
