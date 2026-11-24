---
atom_family: SPEC
atom_id: AN-S-3352
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3083@6
  - AN-S-3016@1-draft
state:
  status: active
  version: 1
  updated_at: "2026-11-22T18:38:16.543046+00:00"
---

## Summary

Report Python wildcard and private imports

## Claim

### Prose Claim

Use declared exports to check private API use. Report wildcard imports as
uncertain when their symbols cannot be resolved. Preserve documented public
re-exports.
