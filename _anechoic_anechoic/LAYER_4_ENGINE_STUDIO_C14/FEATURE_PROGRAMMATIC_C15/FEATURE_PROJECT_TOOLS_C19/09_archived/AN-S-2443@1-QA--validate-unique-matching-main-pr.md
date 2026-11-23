---
atom_family: SPEC
atom_id: AN-S-2443
container:
  component: C19
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 19:05:35 +0400
---
## Summary

Validate unique matching `main` PR

# Summary

Validate unique matching `main` PR

## Scope

one public-release PR discovery and update.

## Claim

**the Operator** **must** verify that zero matching PRs permits creation only after the initial push, one matching PR is reused, and duplicate, retargeted, closed, or URL-changed results stop before further material preparation or remote effects.

## Details

The final refresh must retain the same actual PR URL returned by the initial upsert.
