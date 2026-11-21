---
atom_family: SPEC
atom_id: AN-S-1956
structure:
  container:
    component: C21
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 25
  updated_at: '2026-11-12T13:30:45.299036+00:00'
---
## Summary

Regenerate the MCP registry deterministically

## Claim

### Prose Claim

MCP registry generation **must** be a programmatic deterministic derivation from `schema_version: 1` capability descriptors in the activated installed runtime. It **must** resolve **and** seal the complete descriptor source frontier before publication, use stable ordering, and produce the same semantic registry from the same descriptors **and** activated Project state. It **must not** read a checkout as a live registry source, maintain a manually edited MCP-core allowlist, or execute a capability while generating the registry.

Repeated generation over an unchanged frontier **must** be idempotent, and volatile execution metadata **must not** change MCP capability identity **or** schema. A changed descriptor frontier requires refreshing the registry before starting a build with those descriptors.

## Details

### Deterministic registry generation

In refresh mode, generate the runtime registration asset from the code-owned provider inventory and canonical descriptors. Derive typed schemas from code models, validate names and descriptors, and verify the deterministic asset before final image identity. In existing mode, carry the matching checkout asset unchanged and verify it before startup. Never read native Atoms or call a capability during generation.

MCP loads the generated asset at startup. A source Atom edit does not change exposure or trigger a generic call-time source scan. Replacing a running implementation requires a normal server/container restart. The ready tools/list export is discovery output, not executable registration input.

Equivalent installed code/inventory produce equivalent bytes. Quarantine capabilities with duplicate identities and other invalid individual descriptors with attributable diagnostics, and publish independently valid descriptors. Generation failure or unresolved generator integrity or common activated descriptor frontier stops delivery before startup. Never fall back to Atom discovery.
