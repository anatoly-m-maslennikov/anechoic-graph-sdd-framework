---
atom_family: SPEC
atom_id: AN-S-2786
container:
  component: C45
tier: 7
context:
  lens: QA
state:
  status: draft
  version: 6
  updated_at: '2026-11-13T22:33:03.971381+00:00'
---
## Summary

Verify relation registry delivery on every image rebuild

## Claim

### Prose Claim

Verify that the selected relation registry reaches the image unchanged through every supported build entry point, including Local Release.

#### Build modes

- Refresh mode compiles the registry before image assembly. A selected Declaration change changes the asset and build identity. Identical inputs yield identical bytes. Compilation failure stops the build.
- Existing mode uses the checkout registry unchanged. A missing asset stops the build. Verify with the ANECHOIC service stopped and no predecessor image.

#### Delivery and runtime

Verify source IDs, Versions, paths and fingerprints in delivered metadata. Project authority carriers remain outside the image context. Verify the installed runtime uses the packaged registry and a Declaration change takes effect after asset refresh and image rebuild.
