---
atom_family: SPEC
atom_id: AN-S-1956
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 26
  updated_at: "2026-11-22T09:27:01.061415+00:00"
---
## Summary

Regenerate the MCP registry deterministically

## Claim

### Prose Claim

Backend must derive its registration asset programmatically and deterministically from `schema_version: 1` capability descriptors in the activated installed runtime. It must resolve and seal the complete descriptor source frontier before publication, use stable ordering, and produce the same semantic registry from the same descriptors and activated Project state. It must not read a checkout as a live registry source, maintain a manually edited MCP-core allowlist, or execute a capability while generating the registry.

Repeated generation over an unchanged frontier must be idempotent. Volatile execution metadata must not change capability identity or schema. A changed descriptor frontier requires a registry refresh before a build with those descriptors. MCP maps Backend's enabled JSON catalog; it does not generate or load the registration asset.

## Details

In refresh mode, Backend generates the runtime registration asset from its code-owned provider inventory and canonical descriptors. It derives typed schemas from code models, validates names and descriptors, and verifies the deterministic asset before final image identity. In existing mode, delivery carries the matching checkout asset unchanged and verifies it before startup. Generation never reads native Atoms or calls a capability.

Equivalent installed code and inventory produce equivalent bytes. Backend quarantines capabilities with duplicate identities or other invalid individual descriptors with attributable diagnostics, and publishes independently valid descriptors. Generation failure or unresolved generator integrity or common activated descriptor frontier stops delivery before startup. A source Atom edit does not change exposure or trigger a generic call-time source scan. Replacing a running implementation requires a normal server or container restart. The ready tools/list export is discovery output, not executable registration input.
