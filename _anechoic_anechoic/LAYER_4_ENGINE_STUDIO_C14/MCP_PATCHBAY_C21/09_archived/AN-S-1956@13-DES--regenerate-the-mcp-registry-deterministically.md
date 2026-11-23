---
atom_family: SPEC
atom_id: AN-S-1956
container:
  component: C21
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Regenerate the MCP registry deterministically

# Regenerate the MCP registry deterministically

MCP registry generation **must** be a programmatic deterministic derivation from `schema_version: 1` capability descriptors in the activated installed runtime. It **must** resolve **and** seal the complete descriptor source frontier before publication, use stable ordering, and produce the same semantic registry from the same descriptors **and** activated Project state. It **must not** read a checkout as a live registry source, maintain a manually edited MCP-core allowlist, or execute a capability while generating the registry.

Repeated generation over an unchanged frontier **must** be idempotent, and volatile execution metadata **must not** change MCP capability identity **or** schema. A changed activated installed image **or** descriptor frontier creates a new registry generation; existing calls remain bound to their captured generation, and notification evidence **must** distinguish an emitted change notice from confirmed client refresh.
