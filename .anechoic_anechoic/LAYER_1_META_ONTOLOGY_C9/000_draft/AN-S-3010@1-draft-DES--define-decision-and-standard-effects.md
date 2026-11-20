---
identity:
  atom_id: AN-S-3010
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:59.022525+00:00'
---
## Summary

Define Decision and Standard effects

## Claim

### Prose Claim

A Decision directly affects a specific part of its owning Component's Realization. A Standard directly affects the whole Realization of its owning Component and all descendant Components. Both have the Realization effect; the Solution and Policy templates have the Specification effect.

## Details

Acceptance: a Decision owned by Component A applies to its specified part of A's Realization; a Standard owned by A covers A's Realization and that of child and deeper descendant Components. A sibling outside A's descendant tree is not included by that Standard's scope.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.
