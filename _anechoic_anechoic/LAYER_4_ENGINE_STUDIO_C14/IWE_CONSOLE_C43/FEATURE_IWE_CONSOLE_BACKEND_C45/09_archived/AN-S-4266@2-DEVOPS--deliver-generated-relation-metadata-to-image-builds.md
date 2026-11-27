---
atom_family: SPEC
atom_id: AN-S-4266
container:
  component: C45
tier: 6
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Deliver generated relation metadata to image builds

## Claim

### Prose Claim

Deliver the relation registry as a deterministic JSON asset. Keep declared names, unqualified inverse bindings, inverse aliases, and source Atom IDs, versions, paths and fingerprints. Do not include a changing generation timestamp in the fingerprint. Identical selected inputs produce identical bytes.

Provide one generator with an explicit selected Project root and output path. Generate the asset before computing the image fingerprint and assembling the build context on every supported image-build path, including local release. Local release also includes and verifies the asset in its staged package, alongside the existing code-owned tool registry. Do not use the post-start discovery catalog as an input.

Include only the generated metadata asset and its digest in the build context and image identity. Project authority files remain outside the image context. A missing or failed required generation prevents that image/package from being accepted; it is not silently replaced by a handwritten or stale list.

At runtime, use the selected Project's admitted declaration capture and the same compiler when relevant declarations change. Reuse existing owner synchronization and derived-asset storage. Keep MCP tool discovery's code/config registry separate; do not restore startup scans of all source Atoms just to register MCP tools.

## Details

The existing image/package identity verification covers the generated asset. Registry metadata does not add a source table, a second source of truth, a scheduler or a service.
