---
atom_family: TKT
atom_id: AN-T-1151
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 20:57:35 +0400
---
## Summary

Replace the Code wrapper with a root Package

# Summary

Replace the Code wrapper with a root Package

## Decision

Use Implementation > Package >@(Package), Implementation > Package > Module, and Implementation > Package > Asset. Remove Code as a kind from this Draft model. Implementation contains the root Package; nested Packages have a Package parent. Every Module and Asset belongs to a Package. Code Unit remains inside Module, specialized as Class and Function. This removes the earlier direct Code-versus-Package Module alternatives. The existing Code Definition is a retirement candidate, not a Draft to promote. Documentation and Resources retain their last agreed placements until separately refined.

## State

Updates review Drafts only. Current sources, code and runtime remain unchanged.
