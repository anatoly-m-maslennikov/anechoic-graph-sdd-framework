---
atom_family: SPEC
atom_id: AN-S-1297
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Externalize a large static mapping

## Claim

### Prose Claim

A changed Python module with a reusable static mapping over 20 entries or 25 lines must externalize it: TOML by default, JSON for schema/interchange, YAML only for a declared distinct feature. Its typed loader validates without changing meaning.
