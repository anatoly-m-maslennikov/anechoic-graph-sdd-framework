---
identity:
  atom_id: AN-T-2037
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:43:47.663665+00:00'
---
## Summary

Image refresh queries only lifecycle placement declarations

## Claim

### Prose Claim

In the ANECHOIC working tree based on commit `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/runtime_images.py`, `ImageManager._generated_assets`, calls the host Workbench schema and relation registry compilers before resolving the predecessor. `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/image_relation_registry.py`, `_compile_generated_asset`, passes the Project root directly to those compilers. `compile_lifecycle_assets` uses the predecessor Workbench query only to select lifecycle placement inputs for the candidate schema.

CA-M-1011@3 requires using the previous ready image's Workbench to select eligible Current Declarations for declaration-derived asset refresh. The relation and Workbench schema refresh still select through host readers. The code-owned Tool registry and existing-assets build have separate input paths under CA-D-720@1.
