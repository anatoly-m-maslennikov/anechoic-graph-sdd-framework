---
atom_family: SPEC
atom_id: AN-S-3065
container:
  component: C51
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-22T22:14:44.859998+00:00"
---

## Summary

Declare FORMAL_MODEL_GENERATOR

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C50',
        name='FORMAL_MODEL_GENERATOR',
        lens_whitelist=['DES', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'imports': [
                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                    'model_field_validation.validate_model_fields',
                    'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations',
                    'current_carriers__pub.read_current_model_carriers',
                    'artifact_metadata.atomic_write',
                    'project_selection.resolve_project',
                    'relation_declaration_catalog__pub.build_relation_declaration_catalog',
                    'ADAPTERS_C30__shared.CEILINGS',
                    'ADAPTERS_C30__shared.ReadContext',
                    'ADAPTERS_C30__shared.open_regular',
                    'FEATURE_TOOLS__shared.resolve_native_project',
                    'atom_reference__pub.derive_atom_ref',
                    'cardinality__pub.cardinality_bounds',
                    'ADAPTERS_C30__shared.matches_named_value',
                    'carrier_read__pub.parse_carrier',
                    'code_access_rules__pub.parse_code_access',
                    'component_manifest__pub.parse_component_manifest_fields',
                    'dataclass_field_contract__pub.validate_field_contracts',
                    'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.resolve_model_claim_reference',
                    'markdown_content__pub.parse_content',
                    'model_class_subject__pub.canonical_model_address',
                    'model_class_subject__pub.model_class_target',
                    'model_class_subject__pub.model_declaration_subject',
                    'model_class_subject__pub.simple_model_address',
                    'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                    'FEATURE_MODEL_VALIDATION__shared.verify_model',
                    'native_carrier_header__pub.native_header_view',
                    'ADAPTERS_C30__shared.CUSTOM_MODEL_DIRECTORY',
                    'ADAPTERS_C30__shared.PROJECT_CONFIG_DIRECTORY',
                    'ADAPTERS_C30__shared.NativeModelClaimError',
                    'ADAPTERS_C30__shared.parse_native_model_claim',
                    'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.lint_native_model_claim',
                    'component_seed_manifest__pub.read_component_seed_manifest',
                    'project_manifest__pub.active_manifest_carriers',
                    'project_manifest__pub.select_manifest_carriers',
                    'project_manifest__pub.manifest_inputs',
                    'project_manifest__pub.manifest_state_fields',
                    'ADAPTERS_C30__shared.order_properties',
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
                ],
            },
            'io': {
                'server': {
                    'standalone_model_generate': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.generate_model',
                        'arguments': ['--project-root', '<project-root>', '--output', '<python-file>'],
                    },
                    'manifest_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler',
                    },
                    'image_model_stage': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage',
                        'arguments': ['<project-root>', '<control-root>', '<timeout-seconds>', '[<previous-image-id>]'],
                    },
                    'image_model_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile',
                    },
                },
                'client': [{'component': 'C45', 'interface': 'previous_image_model_claim_selection'}],
            },
            'state': {
                'reads': ['active Project, Component and Component Seed manifests', 'admitted Model claims', 'previous-image claim selection'],
                'writes': ['generated Model package and metadata', 'private Model staging files'],
            },
        },
    ),
)
```
