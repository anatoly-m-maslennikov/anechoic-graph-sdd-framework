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
  version: 4
  updated_at: '2026-11-26T23:28:14.968347+00:00'
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
 'state': {'reads': ['compiled runtime assets', 'pinned Project Spec snapshot'], 'writes': ['private staged Model descriptor']}}
```

## Component Contract

### Prepare a managed Project

Select a receipt-bound Model asset or the bundled Model and report the
fallback. Use one ingested snapshot for the Model and Structure builds.
Return the candidate after both are ready. Runtime admission publishes it.

```python trace
declare_trace_contract(action='prepare_spec_engine', cases={
    'ready': {
        'must_effect': (('C75.bootstrap_model', 'selected'), ('C95.source_snapshot', 'ready'),
                        ('C75.model_inputs', 'admitted'), ('C75.structure_inputs', 'admitted'),
                        ('C93.structure_snapshot', 'ready'), ('C75.compiled_candidate', 'ready')),
        'must_precede': ((('C75.bootstrap_model', 'selected'), ('C95.source_snapshot', 'ready')),
                         (('C95.source_snapshot', 'ready'), ('C75.model_inputs', 'admitted')),
                         (('C75.model_inputs', 'admitted'), ('C75.structure_inputs', 'admitted')),
                         (('C75.structure_inputs', 'admitted'), ('C93.structure_snapshot', 'ready')),
                         (('C93.structure_snapshot', 'ready'), ('C75.compiled_candidate', 'ready'))),
        'same_values': ((('C95.source_snapshot', 'snapshot_id'), ('C75.model_inputs', 'snapshot_id')),
                        (('C95.source_snapshot', 'snapshot_id'), ('C75.structure_inputs', 'snapshot_id'))),
        'value_types': {
            ('C95.source_snapshot', 'snapshot_id'): 'nonempty_string',
            ('C75.model_inputs', 'snapshot_id'): 'nonempty_string',
            ('C75.structure_inputs', 'snapshot_id'): 'nonempty_string',
        },
    },
    'failed': {'forbid_effect': ('C75.compiled_candidate',)},
})
```

### Select the bootstrap Model

Observe the runtime asset admission result. Use the bundled Model only
after a refusal or miss is reported with a reason.

```python trace
declare_trace_contract(action='select_bootstrap_model', cases={
    'receipt': {
        'must_effect': (('C75.bootstrap_model', 'selected', {'source': 'receipt'}),),
        'forbid_effect': ('C75.bootstrap_fallback',),
    },
    'bundled': {
        'must_effect': (('C75.bootstrap_fallback', 'reported'),
                        ('C75.bootstrap_model', 'selected', {'source': 'bundled'})),
        'must_precede': ((('C75.bootstrap_fallback', 'reported'), ('C75.bootstrap_model', 'selected')),),
        'value_types': {('C75.bootstrap_fallback', 'reason'): 'nonempty_string'},
    },
    'failed': {'forbid_effect': ('C75.bootstrap_model',)},
})
```

### Verify Component Specs

Use exact source pins. Return the comparison and source-linked findings.
Report incomplete if the declarations or their translation prevent comparison.

```python trace
declare_trace_contract(action='verify_formal_chain', cases={
    'compared': {'must_effect': (('C94.formal_verification', 'compared'),)},
    'incomplete': {'forbid_effect': ('C94.formal_verification',)},
})
```

### Generate framing tests

Return byte inputs and expected bounds and body for Python framing tests.
Raise a source or declaration error when the pinned chain cannot produce cases.

```python trace
declare_trace_contract(action='generate_framing_cases', cases={
    'generated': {'must_effect': (('C94.generated_cases', 'ready'),)},
    'invalid': {'forbid_effect': ('C94.generated_cases',)},
})
```
