---
atom_family: SPEC
atom_id: AN-S-6
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Classify relocation with update

# Classify relocation with update

## Claim checked

one file identity that changes Structural location **and** also changes content, filename, **or** other governed carrier state is classified as one `MOVE+UPDATE` change set.

## Test case

supply a trigger for one identity whose directory **and** governed content both change **in** the same working-tree transition.

## Acceptance criteria

the sealed context reports exactly `MOVE+UPDATE`, records both paths **and** the resulting version, **and** resolves upstream relations from the observed candidate result graph bound into the provisional context.

## Failure disposition

reject classification **and** report **any** split into two actions, missing flag, identity split, **or** incorrect relation source.

## Observation boundary

the candidate result graph is a read-only description of the observed change, **not** an instruction **to** stage it. capture **any** existing Git index separately; do **not** assume that the final gate already staged the candidate. COMMIT_CONTEXT performs no index mutation **and** grants no Git effect permission. COMMIT_CHANGE_SET alone stages the admitted target **and** revalidates its actual complete staged set at the effect boundary under CA-R-805.
