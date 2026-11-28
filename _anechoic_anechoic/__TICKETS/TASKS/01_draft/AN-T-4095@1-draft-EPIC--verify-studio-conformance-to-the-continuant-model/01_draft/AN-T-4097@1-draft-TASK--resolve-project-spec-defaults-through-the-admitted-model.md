---
atom_family: TKT
atom_id: AN-T-4097
container:
  atom: AN-T-4095
priority: 2
context:
  template: task
  label: Task
state:
  status: draft
  version: 1
  updated_at: '2026-11-28T09:00:23.658085+00:00'
---

## Summary

Resolve Project SPEC defaults through the admitted Model

## Finding

When Project SPEC lifecycle preflight receives an unbound validator,
it can supply the built-in Axiom Tier 0. The admitted Model can declare
a different Tier, as demonstrated by AN-T-4095.

## Acceptance

For a Project with an admitted Model, creation and validation use its
Template constraints and defaults. A missing Model fails explicitly
on that path. Verify a Project Config Tier change through the real
lifecycle entry point. Account for any legacy bootstrap case.

## Implementation

Project SPEC lifecycle now requires a bound Model validator. The
lifecycle code no longer supplies Tier or Lens rules for known
Templates. The replay created Axiom Drafts at Tiers 0 and 1 from
their respective admitted Models. An unbound validator failed before
any carrier write.
