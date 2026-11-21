---
atom_family: SPEC
atom_id: AN-S-2525
container:
  component: C45
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:27:40.868534+00:00'
---
## Summary

Deliver one SQL row per Atom carrier

## Claim scope

The Workbench `atoms` table.

## Claim

### Prose Claim

Key `atoms` by `(relative_path, filename)` so readable carriers with the same logical identity remain separate rows. Publish typed Header and Content columns, one projected `header.relations` JSON value and a deterministic hash of each row excluding its hash field.
