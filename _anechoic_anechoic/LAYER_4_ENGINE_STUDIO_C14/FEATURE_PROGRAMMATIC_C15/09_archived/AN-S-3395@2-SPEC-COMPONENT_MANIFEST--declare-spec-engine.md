---
atom_family: SPEC
atom_id: AN-S-3395
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-26T21:23:05.429250+00:00'
---
## Summary

Declare Spec Engine

## Purpose

Compile the Formal Model and Project Structure, and verify authored
Component Specs. Each branch owns its declarations and uses source Adapters
to read their carriers.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C75',
    name='SPEC_ENGINE',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'exports': {'_package__shared.export_openapi': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.generate_framing_cases': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      '_package__shared.compare_trace_values': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.compile_workflow': {'shared': ['C61',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_LEAN_TRANSLATOR_C84/LEAN_TRANSLATOR_C84__tests/functional',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.verify_formal_chain': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']}},
          'imports': ['C30',
                      'FEATURE_TOOLS__shared.resolve_native_project',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.load_native_model',
                      'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                      'manifest_compiler_CS1__shared.compile_ingested_cli',
                      'manifest_compiler_CS1__shared.write_model',
                      'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure',
                      'LAYER_2_PROJECT_STRUCTURE_C93__rows.compile_structure_rows',
                      'C95',
                      'C75',
                      'C83',
                      'C84',
                      'C85',
                      'C86',
                      'C87',
                      'C88',
                      'C89',
                      'C90',
                      'C92']},
 'io': {'server': {'compile_project': {
     'transport': 'cli',
     'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub',
 }}}}
```

## Component Contract

### Spec Engine responsibilities

#### Guarantee

Keep Model manifests, Structure manifests, and Component
Boundaries, Contracts, and Solutions on their respective workflows.
Verify the exact pinned Component Specs and report incomplete evidence.
