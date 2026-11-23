---
atom_family: SPEC
atom_id: AN-S-4733
concern:
  components:
  - C63
  - C81
container:
  component: C63
tier: 2
context:
  template: STANDARD
  lens: DevOps
relations:
  CONTRIBUTES_TO:
  - AN-S-3380
state:
  status: active
  version: 1
  updated_at: '2026-11-23T14:45:10.920666+00:00'
---

## Summary

Retain resources after Local Release promotion

## Claim

### Prose Claim

Keep the current production image and up to two prior Project-owned production
images. Remove eligible unused test images and proven obsolete Project
resources. Protect resources that containers reference and test images in use
by active releases. Report unverified ownership and failed cleanup.

After promotion, prune Docker build cache toward at most 4 GB used and at least
2 GB free. Purge temporary paths older than 48 hours. Preserve shared locks,
managed tool caches, and resumable Atom Review state.
