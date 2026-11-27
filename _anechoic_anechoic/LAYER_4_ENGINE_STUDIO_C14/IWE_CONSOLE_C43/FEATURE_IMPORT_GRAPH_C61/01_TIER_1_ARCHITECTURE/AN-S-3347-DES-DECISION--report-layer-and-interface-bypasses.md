---
atom_family: SPEC
atom_id: AN-S-3347
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-26T16:38:46.247943+00:00'
---
## Summary

Report layer and interface bypasses

## Claim

### Prose Claim

Use the Realization Graph to report denied imports, unresolved owners, and declared exceptions separately. Check entry ownership under AN-S-3179. Report imports that forward someone else's symbol through an intermediate Package.

For each Package, report external imports that resolve outside the Project and exclude language built-ins. Keep unresolved imports in their own report.

Require zero forbidden imports in Beta before promotion. Track allowed bypasses for review even when Beta passes.
