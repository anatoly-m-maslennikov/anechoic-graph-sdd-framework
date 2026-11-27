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
  status: draft
  version: 3
  updated_at: '2026-11-26T21:59:37.736957+00:00'
---
## Summary

Declare Spec Engine

## Purpose

Admit the runtime Model, coordinate Project Spec compilation, and verify authored Component Specs.

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
 }}},
 'state': {'reads': ['compiled runtime assets', 'pinned Project Spec snapshot'], 'writes': []}}
```

## Component Contract

### Spec engine responsibilities

#### Guarantee

Load the admitted compiled Model from `.anechoic_runtime/assets/`. If admission fails, report the reason and use the Model bundled in the image. Wait for the Project Spec snapshot in DuckDB before compiling or verifying authored declarations. The ingestion worker owns authored Markdown reads.

```python trace
declare_trace_contract(
    action='prepare_spec_engine',
    cases={
        'ready': {'must_effect': (
            ('C75.bootstrap_model', 'selected'),
            ('C95.source_snapshot', 'ready'),
        ), 'must_precede': (
            (('C75.bootstrap_model', 'selected'), ('C95.source_snapshot', 'ready')),
        )},
        'failed': {'forbid_effect': ('C75.spec_engine',)},
    },
)
```
