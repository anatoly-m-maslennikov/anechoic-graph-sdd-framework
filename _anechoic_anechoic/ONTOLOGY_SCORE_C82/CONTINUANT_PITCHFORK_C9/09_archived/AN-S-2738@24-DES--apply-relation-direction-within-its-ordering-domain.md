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
  version: 24
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Apply relation direction within its ordering domain

# Summary

Apply relation direction within its ordering domain

## Scope

declared relations.

## Claim

**every** declared relation **must** satisfy the target position **and** ordering domain registered for its relation family. Stored governing RMED relation occurrences selected by CA-R-2148 **must** use the numeric Tier-and-Scope ordering in CA-R-2149: a same-Scope target **must** have a strictly lower numeric Tier, a target in a strict ancestor Scope Unit is accepted without Tier comparison, and a descendant **or** sibling target is forbidden. Temporal relations **must** use lifecycle succession, realization relations **must** use realization order, dependency relations **must** use dependency order, **and** **every** other admitted domain **must** use its own registered order. a universal upstream **or** downstream rule **must not** be inferred across different ordering domains, **and** an inverse-derived view **must not** create another declared edge.

## Details

For selected governing RMED occurrences, CA-D-637 defines the ordering context of a verified Project Goal without treating its Operator owner as a Scope Unit. Ordinary endpoints still use their Local Scope Unit.
