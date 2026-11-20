---
atom_family: SPEC
atom_id: AN-S-2786
structure:
  container:
    component: C45
  tier: 7
context:
  lens: QA
state:
  status: active
  version: 5
  updated_at: '2026-11-12T12:29:30.190837+00:00'
---
## Summary

Verify relation registry delivery on every image rebuild

## Claim

### Prose Claim

Verify the selected relation registry reaches the image unchanged for every supported build entry point, including Local Release.

- In refresh mode, compile the registry before image assembly. A selected Declaration change changes asset and build identity. Identical inputs yield identical bytes. A compilation failure stops the build.
- In existing mode, use the checkout registry unchanged. A missing asset stops the build. Verify this mode with the ANECHOIC service stopped and without a predecessor image.

Verify the source IDs, Versions, paths and fingerprints in the delivered metadata. Keep Project authority carriers outside the image context. Verify the installed runtime uses the packaged registry and that a Declaration change takes effect after asset refresh and image rebuild.
