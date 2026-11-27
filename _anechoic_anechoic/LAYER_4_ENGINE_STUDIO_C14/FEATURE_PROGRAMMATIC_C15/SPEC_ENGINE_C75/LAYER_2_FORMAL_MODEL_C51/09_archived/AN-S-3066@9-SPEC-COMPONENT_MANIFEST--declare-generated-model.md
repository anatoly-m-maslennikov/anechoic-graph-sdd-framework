---
atom_family: SPEC
atom_id: AN-S-3066
container:
  component: C51
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 9
  updated_at: "2026-11-26T15:52:29.816992+00:00"
---

## Summary

Declare GENERATED_MODEL

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C52',
    name='GENERATED_MODEL',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['FEATURE_GENERATED_MODEL_C52__shared.Atom',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomContent',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomContext',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomHeader',
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomTier',
                      'FEATURE_GENERATED_MODEL_C52__shared.Plan'],
          'exports': {'FEATURE_GENERATED_MODEL_C52__shared.Atom': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomContent': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomContext': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomHeader': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomTier': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.Plan': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.PlanForm': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.WorkReport': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestination': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']},
                      'FEATURE_GENERATED_MODEL_C52__shared.AtomDestinationFile': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_MODEL_VALIDATION/FEATURE_MODEL_VALIDATION__tests']}}}}
```

## Component Contract

### Supply the bundled Model classes

#### Guarantee

Provide the bundled Python Model classes to admitted consumers. An Atom
has separate Header and Content fields with the bundled field contracts.
Plan is an Atom subtype and uses the same fields.

#### References

AN-S-2288, AN-S-3066, and AN-T-2947.
