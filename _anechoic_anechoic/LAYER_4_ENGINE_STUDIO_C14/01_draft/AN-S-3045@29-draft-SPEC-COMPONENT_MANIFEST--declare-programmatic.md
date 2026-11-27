---
atom_family: SPEC
atom_id: AN-S-3045
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 29
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Declare PROGRAMMATIC

## Purpose

Group Programmatic Components and compile Python Model Claim fences.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C15',
    name='PROGRAMMATIC',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.lint_python_model_claim',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compile_python_model_claim',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compile_atom_dependencies_with_check',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.ScopeUnit',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.check_scope_levels_with_packaged_check',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.generated_assets',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.load_packaged_module',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.verify_packaged_assets',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.write_package',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.Atom',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.dependencies_are_distinct',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.verify_packaged_dependencies_check',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compiler_model_statements',
                      'ADAPTERS_C30__shared.parse_component_manifest',
                      'ADAPTERS_C30__shared.parse_component_manifest_fields',
                      'ADAPTERS_C30__shared.ScopeUnitDeclaration',
                      'ADAPTERS_C30__shared.PythonModelClaimError',
                      'ADAPTERS_C30__shared.iter_formal_claims',
                      'ADAPTERS_C30__shared.parse_grouped_python_model_claim',
                      'ADAPTERS_C30__shared.parse_structured_python_model_claim',
                      'ADAPTERS_C30__shared.content_key',
                      'ADAPTERS_C30__shared.formal_claim_fences',
                      'ADAPTERS_C30__shared.parse_carrier',
                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                      'topic_dependencies__pub.DEPENDENCIES_CHECK_SOURCE_SHA256',
                      'topic_dependencies__pub.validate_dependencies_claim',
                      'dataclass_field_contract__pub.has_dataclass_field_contracts',
                      'dataclass_field_contract__pub.validate_field_contracts',
                      'ADAPTERS_C30__shared.canonical_model_address',
                      'ADAPTERS_C30__shared.simple_model_address',
                      'placement_claim__pub.parse_placement_rules',
                      'ADAPTERS_C30__shared.formal_claim',
                      'ADAPTERS_C30__shared.class_bindings',
                      'ADAPTERS_C30__shared.parse_native_model_claim',
                      'ADAPTERS_C30__shared.validate_aspect_hierarchy',
                      'ADAPTERS_C30__shared.validate_aspect_instance',
                      'ADAPTERS_C30__shared.ScopeUnitDeclarations',
                      'ADAPTERS_C30__shared.is_current_requirement_declaration',
                      'legacy_relation__pub.emits_instance_inverse',
                      'ADAPTERS_C30__shared.model_class_target',
                      'ADAPTERS_C30__shared.parse_python_model_claim',
                      'ADAPTERS_C30__shared.Span',
                      'ADAPTERS_C30__shared.Name',
                      'ADAPTERS_C30__shared.ValueLiteral',
                      'ADAPTERS_C30__shared.FormatReference',
                      'ADAPTERS_C30__shared.Cardinality',
                      'ADAPTERS_C30__shared.Qualification',
                      'ADAPTERS_C30__shared.DeclaredReference',
                      'ADAPTERS_C30__shared.SelectionGroup',
                      'ADAPTERS_C30__shared.SelectionSuffix',
                      'ADAPTERS_C30__shared.PathStep',
                      'ADAPTERS_C30__shared.Path',
                      'ADAPTERS_C30__shared.RelationLink',
                      'ADAPTERS_C30__shared.RelationChain',
                      'ADAPTERS_C30__shared.ParsedSubject',
                      'ADAPTERS_C30__shared.parse_subject_expression',
                      'ADAPTERS_C30__shared.render_subject',
                      'ADAPTERS_C30__shared.GrammarSource',
                      'ADAPTERS_C30__shared.GrammarPin',
                      'ADAPTERS_C30__shared.InitialAtomSelector',
                      'ADAPTERS_C30__shared.SubjectNotationError',
                      'ADAPTERS_C30__shared.SubjectProfile',
                      'ADAPTERS_C30__shared.get_profile',
                      'ADAPTERS_C30__shared.namespace_local_expression',
                      'ADAPTERS_C30__shared.parse_initial_atom_selector',
                      'ADAPTERS_C30__shared.parse_subject',
                      'ADAPTERS_C30__shared.profile_evidence',
                      'carrier_read__pub.parse_carrier',
                      'ADAPTERS_C30__shared.carrier_read_view',
                      'ADAPTERS_C30__shared.matches_named_value',
                      'ADAPTERS_C30__shared.named_value_token'],
          'exports': {'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.lint_python_model_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compile_python_model_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compile_atom_dependencies_with_check': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.ScopeUnit': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.check_scope_levels_with_packaged_check': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.generated_assets': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.load_packaged_module': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.verify_packaged_assets': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.write_package': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.compiler_model_statements': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.resolve_model_claim_reference': {'private': ['C50']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.lint_native_model_claim': {'private': ['C50']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.formal_claim_blocks': {'private': ['C59',
                                                                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND',
                                                                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.Atom': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.DEPENDENCIES_CLAIM_SHA256': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.dependencies_are_distinct': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                                'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']},
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.verify_packaged_dependencies_check': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests',
                                                                                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE/FEATURE_FORMAL_MODEL_ENGINE__tests']}}},
 'io': {'server': {'compile_formal_claim': {'outcomes': {'python_statements_returned': {'must_effect': [['C15.model_statements',
                                                                                                         'compiled']]},
                                                         'empty_blocks_returned': {'must_effect': [['C15.model_statements',
                                                                                                    'compiled']]},
                                                         'no_statements': {'forbid_effect': ['C15.model_statements']},
                                                         'compilation_error': {'must_effect': [['C15.compilation_error',
                                                                                                'reported']],
                                                                               'forbid_effect': ['C15.model_statements']}}}}}}
```

## Component Contract

### Compile formal Model Claim blocks

Read the formal Claim fences of one supplied Atom body. Return one block
per selected Python fence, in body order. Join the compiled statements
in each block with a semicolon and newline. A selected fence that
compiles to zero statements yields an empty block. Unsupported fences
yield no blocks. If compilation fails, report the error and return no
result. The optional typed-property skip excludes matching fences.

`no_statements` means no fences were selected. `empty_blocks_returned`
means at least one fence was selected and all compiled to zero statements.
`python_statements_returned` means at least one statement was compiled.
The compiled effect records completion, including an empty compilation.

```python trace
declare_trace_contract(
    action='compile_formal_claim',
    cases={
        'python_statements_returned': {
            'must_effect': (('C15.model_statements', 'compiled'),),
        },
        'empty_blocks_returned': {
            'must_effect': (('C15.model_statements', 'compiled'),),
        },
        'no_statements': {'forbid_effect': ('C15.model_statements',)},
        'compilation_error': {
            'must_effect': (('C15.compilation_error', 'reported'),),
            'forbid_effect': ('C15.model_statements',),
        },
    },
)
```

## Details

The Formal Model Engine belongs to C15. C15 delegates Model generation, bundled classes, and Model validation to C51 and its children. Existing code grants above remain in force.
