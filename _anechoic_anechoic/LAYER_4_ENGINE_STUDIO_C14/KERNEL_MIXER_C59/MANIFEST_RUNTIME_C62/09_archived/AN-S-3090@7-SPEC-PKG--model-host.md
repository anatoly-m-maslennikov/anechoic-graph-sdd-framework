---
atom_family: SPEC
atom_id: AN-S-3090
container:
  component: C62
tier: 2
context:
  template: PKG
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-22T08:01:52.246620+00:00"
---

## Summary

Model Host

## Purpose

Provide the loaded Model to implementation and validators.

## Contract

Verify the compiler-attested descriptor and Model module bytes. Bind
the generated types and reviewed checks in a namespace owned by that
generation. Keep an admitted generation available for its consumers'
lifetime.

Provide one bound reviewed Model per process for Project discovery and
startup. Prepare it through the short-lived compiler.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(
    entity_name="Package Spec",
    instance=PackageSpec(
        package_id="pkg2",
        boundaries={"code": {"exports": {
            "model_host_pkg2__pub.reviewed_native_model": {
                "private": [
                    "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP",
                    "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests",
                    "C59",
                    "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests",
                ],
            },
        }}},
    ),
)
```
