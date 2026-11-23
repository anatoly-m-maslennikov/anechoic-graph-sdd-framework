---
atom_family: TKT
atom_id: AN-T-3467
container:
  component: C20
priority: 2
context:
  template: problem
state:
  status: archived
  version: 2
  updated_at: 2026-10-04 22:52:48 +0000
---
## Summary

Align selected queue admission with fifteen-route scope

## Concern

The accepted MCP contract expands the selected Epic to fifteen routes, but CA-D-521@3 closes enqueue_selected admission to only thirteen registrations. Implementing the two additional routes through the existing queue requires its source admission amendment first.

## Evidences

CA-D-521's Scope and enqueue_selected paragraph explicitly say thirteen. CA-P-1543 accepts the fifteen-route MCP source but correctly does not claim current queue admission/runtime registration. CA-P-1551/1552 bind the narrow source amendment and independent acceptance.

## Blast radius

Resolved disposition: D521@5 now agrees with R1847's exact two query admission frontiers and retains all original guards. Independent P1552@3 accepts this source-only repair. P1562/P1563 still own actual manifest/handler integration.

Query queue integration stays gated until current Delivery authority admits the exact same fifteen-route canonical manifest. No code silently widens the closed source contract or creates a second executor.
