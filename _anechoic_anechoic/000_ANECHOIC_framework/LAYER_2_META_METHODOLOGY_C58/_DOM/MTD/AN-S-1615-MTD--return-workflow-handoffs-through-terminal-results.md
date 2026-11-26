---
atom_family: SPEC
atom_id: AN-S-1615
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: active
  version: 23
  updated_at: '2026-11-25T21:47:22.502720+00:00'
---
## Summary

Return Workflow handoffs through terminal results

## Claim

### Prose Claim


Workflow handoffs to another Workflow.


**when** a Workflow declares a handoff **to** another Workflow, its Run **must** end with a terminal result sufficient for the executor **to** evaluate **and** start the continuation separately.

## Details

### Handoff result

- identify the completed Run, the reason for handoff, **and** the continuation Workflow **or** the methodology rule that selects it.
- provide the target identities **and** observed Revisions, required inputs **and** parameters, proposed changes, completed checks **and** their applicability, **and** a complete account of effects already performed, **if** **any**.
- distinguish a requested continuation from an authorized, started, **or** completed continuation. an incomplete result **must not** trigger guessed execution.

### Run boundary

- the ending Run does **not** call the continuation Workflow, wait for it, **or** resume its own normal Steps afterward.
- the executor retains the original request **and** the association between predecessor **and** successor Runs; it rechecks applicable authority **and** input freshness **before** starting the successor.
- ending the predecessor **must not** report the requested work as complete **when** a required continuation is still pending, blocked, **or** failed.
- the handoff outcome does **not** itself add a Status value. a chain of handoffs **must not** bypass approval, refresh an exhausted retry allowance, **or** create an unbounded loop.

the handoff is a result between distinct Runs, **not** a Step route between different Workflows.
