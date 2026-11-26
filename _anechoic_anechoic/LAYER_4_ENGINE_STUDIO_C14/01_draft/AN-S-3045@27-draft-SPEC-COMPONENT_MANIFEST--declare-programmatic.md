---
atom_family: SPEC
atom_id: AN-S-3045
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 27
  updated_at: '2026-11-25T16:16:40+00:00'
---

## Summary

Declare PROGRAMMATIC

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C15',
        name='PROGRAMMATIC',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
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
                    'ADAPTERS_C30__shared.named_value_token',
                    'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.NativeModelClaimError',
                ],
            },
            'io': {
                'server': {
                    'compile_formal_claim': {'outcomes': {
                        'python_statements_returned': {'must_effect': (('C15.model_statements', 'python'),)},
                        'cfel_statements_returned': {'must_effect': (('C15.model_statements', 'comment_free_cfel'),)},
                        'compilation_error': {'must_effect': (('C15.compilation_error', 'reported'),), 'forbid_effect': ('C15.model_statements',)},
                        'no_statements': {'forbid_effect': ('C15.model_statements',)},
                    }},
                },
            },
        },
    ),
)
```

## Details

The Formal Model Engine belongs to C15. C15 delegates Model generation, bundled classes, and Model validation to C51 and its children. Existing code grants above remain in force.
