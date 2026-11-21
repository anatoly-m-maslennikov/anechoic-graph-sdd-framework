---
atom_family: SPEC
atom_id: AN-S-1992
structure:
  container:
    component: C15
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 33
  updated_at: '2026-11-20T11:29:16.594181+00:00'
---

## Summary

Read Engine settings through one shared boundary

## Claim

When PROGRAMMATIC behavior depends on Project settings, every applicable Tool, App and MCP component uses one shared Reader for the authoritative Project Manifest. The Reader validates the complete input and returns an immutable typed snapshot of actual values, the exact selected Project, physical source path, raw SHA-256 Digest and declared schema marker. It does not query the Work Journal or determine logical Revision or currentness. The snapshot is derived and is not a Projection.

The Reader and dedicated write operation use one shared Carrier adapter bound to the exact authoritative Manifest. The adapter writes only a complete validated document supplied by that operation; validation failure leaves the file unchanged. Pass the snapshot explicitly to consumers; do not add component-specific parsers, defaults, environment fallbacks, semantic overrides or Reader writes. The control panel uses the same Reader and requests changes through the dedicated write operation. Stop for a missing or invalid Manifest, absent path or Digest provenance, or a consumer that bypasses or mutates the snapshot.
