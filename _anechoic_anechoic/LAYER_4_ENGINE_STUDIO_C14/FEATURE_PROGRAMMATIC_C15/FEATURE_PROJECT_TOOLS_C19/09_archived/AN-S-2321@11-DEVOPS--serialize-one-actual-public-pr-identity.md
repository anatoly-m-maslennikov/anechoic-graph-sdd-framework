---
atom_family: SPEC
atom_id: AN-S-2321
container:
  component: C19
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Serialize one actual public PR identity

# Summary

Serialize one actual public PR identity

## Scope

the PR result of one public-release remote action.

## Claim

public PR evidence **must** retain one actual HTTPS PR URL, positive PR number, open Draft state, `amm/dev` head, `main` base, and repository-relative Tool-call result reference.

## Details

This representation records PR maintenance only. A created PR is Draft, and an existing open PR is converted to Draft before its body is edited. It contains no merge effect, merge receipt, or target-branch adoption claim.
