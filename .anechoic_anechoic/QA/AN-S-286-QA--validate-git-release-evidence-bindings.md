---
identity:
  atom_id: AN-S-286
context:
  container:
    component: C00
  tier: 2
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-10-27 19:59:35 +0400
---
## Summary

Validate Git release evidence bindings

# Validate Git release evidence bindings

## Cases

1. encode one repository **and** the full commit object ID of the evaluated candidate.
2. supply a branch name, HEAD, **or** tag label **without** its resolved commit ID.
3. retain a tag label with its resolved commit ID, **then** move the tag **or** branch.
4. evaluate changed working-tree content **and** attempt **to** identify it **only** by the earlier commit ID.
5. inspect release references recorded through the existing Journal **and** proof-frontier Carriers.

## Acceptance

case 1 passes the exact-reference check. case 2 fails. case 3 retains the original immutable binding rather than following the changed label. case 4 fails the claimed committed-content binding **unless** the selected representation explicitly identifies the actual candidate differences. case 5 introduces no second authoritative release log **or** competing Journal schema.

## Failure disposition

identify the exact invalid binding **and** block reliance on that evidence. these cases authorize no commit, tag, merge, push, **or** release operation.
