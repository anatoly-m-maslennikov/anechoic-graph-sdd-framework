---
atom_family: SPEC
atom_id: AN-S-1956
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Regenerate the MCP registry deterministically

## Claim

### Prose Claim

MCP registry generation **must** be a programmatic deterministic derivation from `schema_version: 1` capability descriptors in the activated installed runtime. It **must** resolve **and** seal the complete descriptor source frontier before publication, use stable ordering, and produce the same semantic registry from the same descriptors **and** activated Project state. It **must not** read a checkout as a live registry source, maintain a manually edited MCP-core allowlist, or execute a capability while generating the registry.

Repeated generation over an unchanged frontier **must** be idempotent, and volatile execution metadata **must not** change MCP capability identity **or** schema. A changed activated installed image **or** descriptor frontier creates a new registry generation; existing calls remain bound to their captured generation, and notification evidence **must** distinguish an emitted change notice from confirmed client refresh.

## Details

### Deterministic registry generation

Every local release and image rebuild, before MCP startup, generate the runtime registration asset from the installed code-owned provider inventory and canonical descriptors. Derive typed schemas from code models, validate names/descriptors, and write deterministic output inside the package before final identity verification; the image build regenerates it from copied Engine code. Never read native Atoms or call a capability during generation.

MCP loads the generated asset at startup. A source Atom edit does not change exposure or trigger a generic call-time source scan. Replacing a running implementation follows explicit restart or optional hot-reload boundaries; hot reload is disabled by default. The ready tools/list export is discovery output, not executable registration input.

Equivalent installed code/inventory produce equivalent bytes. Quarantine capabilities with duplicate identities and other invalid individual descriptors with attributable diagnostics, and publish independently valid descriptors. Generation failure or unresolved generator integrity or common activated descriptor frontier stops delivery before startup. Never fall back to Atom discovery.
