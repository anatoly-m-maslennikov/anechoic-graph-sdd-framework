---
atom_family: SPEC
atom_id: AN-S-3090
container:
  component: C62
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: "active"
  version: 11
  updated_at: "2026-11-24T20:16:08.279131+00:00"
---

# Model Host

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name="Component Seed Manifest",
    instance=ComponentSeedManifest(
        component_seed_id="CS2",
        boundaries={
            "code": {
                "imports": ["MANIFEST_RUNTIME_C62__shared.compile_reviewed_model"],
                "exports": {
                    "model_host_CS2__shared.reviewed_native_model": {
                        "private": [
                            "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP",
                            "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests",
                            "C45",
                            "C59",
                            "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/MANIFEST_RUNTIME_C62/MANIFEST_RUNTIME_C62__tests",
                            "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/MANIFEST_RUNTIME_C62/model_host_CS2/model_host_CS2__tests",
                            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests",
                        ],
                    },
                }
            }
        },
    ),
)
```

## Purpose

Provide the loaded Model to implementation and validators.

## Solution

Verify the compiler-attested descriptor and Model module bytes. Bind
the generated types and reviewed checks in a namespace owned by that
generation. Keep an admitted generation available for its consumers'
lifetime.

Provide one bound reviewed Model per process for Project discovery and
startup. Prepare it through the short-lived compiler.
