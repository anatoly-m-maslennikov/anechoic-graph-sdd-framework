---
atom_family: SPEC
atom_id: AN-S-1933
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 8
  updated_at: "2026-11-23T01:48:06.181628+00:00"
---
## Summary

Carry code-owned MCP registration in the installed package

## Claim

### Prose Claim

Backend carries the code-owned provider inventory and generated registration asset. Generate the asset from installed provider descriptors and canonical models under AN-S-1956. MCP maps Backend's enabled JSON catalog; it does not generate or load that asset.

In refresh mode, generate and verify the asset before final package and image identity. In existing mode, carry the matching checkout asset unchanged and verify it before startup. Failed generation, verification or unresolved common descriptor frontier stops delivery before startup.

Keep the protocol interface declaration version-bound, including supported capabilities and result meanings. Derive schemas from canonical models; keep declarations, schemas and examples credential-free. Registration and schema generation do not execute capabilities or grant effect permission.
