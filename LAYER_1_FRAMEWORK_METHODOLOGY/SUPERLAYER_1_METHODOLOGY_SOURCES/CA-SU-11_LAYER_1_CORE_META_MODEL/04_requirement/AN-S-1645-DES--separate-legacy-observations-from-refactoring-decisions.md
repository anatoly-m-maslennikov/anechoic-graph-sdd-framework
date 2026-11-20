---
identity:
  atom_id: AN-S-1645
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 28
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Separate legacy observations from refactoring decisions

## Claim

### Prose Claim


Reverse-engineering results, including observed Implementation facts and proposed decisions about the intended refactored result.


reverse-engineering results **must** distinguish observed Implementation facts from proposed decisions about the intended refactored result.

- behavior **or** constraints proposed for preservation **must** be identified as proposed decisions.
- behavior **or** constraints proposed for change **must** be identified as proposed decisions.
- unresolved behavior, missing evidence, **and** uncertain interpretations **must** remain explicit.

an observed behavior **or** defect **must not** become a Requirement merely because it exists **in** the legacy Implementation. supporting evidence **must** remain recoverable **without** a proposed disposition **or** uncertainty being presented as an observed fact.
