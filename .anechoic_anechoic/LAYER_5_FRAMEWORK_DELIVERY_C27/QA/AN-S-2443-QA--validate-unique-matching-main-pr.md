---
identity:
  atom_id: AN-S-2443
context:
  container:
    component: C27
  tier: 5
  lens: QA
state:
  status: active
  version: 12
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Validate unique matching `main` PR

## Scope

one public-release PR discovery and update.

## Claim

### Prose Claim

**the Operator** **must** verify that zero matching PRs permits creation only after the initial push, one matching PR is reused, and duplicate, retargeted, closed, or URL-changed results stop before further material preparation or remote effects.

## Details

The final refresh must retain the same actual PR URL returned by the initial upsert.
