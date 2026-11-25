---
atom_family: SPEC
atom_id: AN-S-2738
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Apply relation direction within its ordering domain

# Summary

Apply relation direction within its ordering domain

## Scope

declared relations.

## Claim

**every** declared relation **must** satisfy the target position **and** ordering domain registered for its relation family. Normative-authority relations **must** use the global-tier **and** authority hierarchy, temporal relations **must** use lifecycle succession, realization relations **must** use realization order, dependency relations **must** use dependency order, **and** **every** other admitted domain **must** use its own registered order. a universal upstream **or** downstream rule **must not** be inferred across different ordering domains, **and** an inverse-derived view **must not** create another declared edge.

## Details
