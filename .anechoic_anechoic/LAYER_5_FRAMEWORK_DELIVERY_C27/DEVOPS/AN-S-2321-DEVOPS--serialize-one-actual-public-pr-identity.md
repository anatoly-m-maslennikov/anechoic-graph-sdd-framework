---
identity:
  atom_id: AN-S-2321
context:
  container:
    component: C27
  tier: 4
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Serialize one actual public PR identity

## Scope

the PR result of one public-release remote action.

## Claim

### Prose Claim

public PR evidence **must** retain one actual HTTPS PR URL, positive PR number, open Draft state, `amm/dev` head, `main` base, and repository-relative Tool-call result reference.

## Details

This representation records PR maintenance only. A created PR is Draft, and an existing open PR is converted to Draft before its body is edited. It contains no merge effect, merge receipt, or target-branch adoption claim.
