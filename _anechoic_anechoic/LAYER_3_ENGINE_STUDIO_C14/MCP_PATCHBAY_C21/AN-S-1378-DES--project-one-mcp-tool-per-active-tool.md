---
atom_family: SPEC
atom_id: AN-S-1378
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 24
  updated_at: "2026-11-22T09:27:00.770047+00:00"
---
## Summary

Project one MCP tool per active Tool

## Claim

### Prose Claim

MCP must expose exactly one callable endpoint for each enabled public Tool name in Backend's JSON catalog. It must preserve the catalog's name, description, input schema, and canonical operation meaning. Backend owns registration, the canonical handler, and the request and result contract. Source-only providers have no public endpoint. Duplicate public identities or missing configured entries must be rejected before publication.

No current Atom declaration is required merely to register or list an implemented, configured Tool.
