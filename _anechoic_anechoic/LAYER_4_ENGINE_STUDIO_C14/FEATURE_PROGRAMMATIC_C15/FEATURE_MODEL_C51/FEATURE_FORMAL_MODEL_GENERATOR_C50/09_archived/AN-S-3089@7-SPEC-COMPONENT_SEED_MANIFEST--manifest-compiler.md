---
atom_family: SPEC
atom_id: AN-S-3089
container:
  component: C50
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-24T21:31:00.821347+00:00"
---

# Manifest Compiler

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name="Component Seed Manifest", instance=ComponentSeedManifest(
        component_seed_id="CS1",
        boundaries={"code": {"imports": [
            "FEATURE_FORMAL_MODEL_GENERATOR__shared._add_unambiguous_addresses",
            "FEATURE_FORMAL_MODEL_GENERATOR__shared._class_property_aliases",
        ], "exports": {
            "manifest_compiler_CS1__shared.bounded_run": {"private": ["LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests"]},
            "manifest_compiler_CS1__shared.previous_claims": {"private": ["LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests"]},
            "manifest_compiler_CS1__shared.stage_model": {"private": ["LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests"]},
            "manifest_compiler_CS1__shared.compile_structure": {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests']},
            "manifest_compiler_CS1__shared.read_active_model_sources": {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
            "manifest_compiler_CS1__shared.render_atom_header_lean": {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
            "manifest_compiler_CS1__shared.verify_model_lean": {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
            "manifest_compiler_CS1__shared.write_model": {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
        }}},
    )
)
```

## Purpose

Compile Active SPEC Manifests and the admitted Model declarations.

## Solution

Run as a short-lived Model Generator worker. Emit Model modules and a JSON descriptor
with admitted bindings, source revisions, and fingerprints. Attest the
descriptor for the launcher. A Structure refresh uses the admitted
descriptor digest and emits a snapshot validated against that Model.

For image admission, compile and verify staged Model sources and return
their fingerprint. With no staged sources, return the reviewed Model
fingerprint.
