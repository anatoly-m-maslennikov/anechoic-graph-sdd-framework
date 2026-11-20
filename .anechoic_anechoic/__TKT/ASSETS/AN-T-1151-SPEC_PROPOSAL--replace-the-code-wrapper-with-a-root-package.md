---
identity:
  atom_id: AN-T-1151
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: active
  version: 2
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Replace the Code wrapper with a root Package

## Decision

Use Implementation > Package >@(Package), Implementation > Package > Module, and Implementation > Package > Asset. Remove Code as a kind from this Draft model. Implementation contains the root Package; nested Packages have a Package parent. Every Module and Asset belongs to a Package. Code Unit remains inside Module, specialized as Class and Function. This removes the earlier direct Code-versus-Package Module alternatives. The existing Code Definition is a retirement candidate, not a Draft to promote. Documentation and Resources retain their last agreed placements until separately refined.

## State

Updates review Drafts only. Current sources, code and runtime remain unchanged.
