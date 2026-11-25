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
  status: draft
  version: 31
  updated_at: '2026-11-24T17:50:59+00:00'
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
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_manifest_property_bearers',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_relation_references',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._class_property_aliases',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._merge_constraint_claims',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._native_claim',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared._native_claim_text',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.admit_active_model_records',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.assemble_model_classes',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.assemble_model_modules',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.build_model_class_source',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.compile_native_bindings',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.load_compiled_model',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.load_native_model',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.model_module_name',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.native_manifest_model',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.reviewed_model_records',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.select_model_claims',
                    'FEATURE_FORMAL_MODEL_GENERATOR__shared.select_model_declarations',
                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                    'model_field_validation.validate_model_fields',
                    'FEATURE_MODEL_VALIDATION__shared.bind_model_declarations',
                    'ADAPTERS_C30__shared.read_current_model_carriers',
                    'FEATURE_TOOLS__shared.atomic_write',
                    'FEATURE_TOOLS__shared.resolve_project',
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
                    'ADAPTERS_C30__shared.parse_content',
                    'ADAPTERS_C30__shared.canonical_model_address',
                    'ADAPTERS_C30__shared.model_class_target',
                    'ADAPTERS_C30__shared.model_declaration_subject',
                    'ADAPTERS_C30__shared.simple_model_address',
                    'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                    'FEATURE_MODEL_VALIDATION__shared.open_serialized_model',
                    'FEATURE_MODEL_VALIDATION__shared.verify_model',
                    'ADAPTERS_C30__shared.native_header_view',
                    'ADAPTERS_C30__shared.canonical_native_header',
                    'ADAPTERS_C30__shared.CUSTOM_MODEL_DIRECTORY',
                    'ADAPTERS_C30__shared.PROJECT_CONFIG_DIRECTORY',
                    'ADAPTERS_C30__shared.NativeModelClaimError',
                    'ADAPTERS_C30__shared.parse_native_model_claim',
                    'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.lint_native_model_claim',
                    'component_seed_manifest__pub.read_component_seed_manifest',
                    'ADAPTERS_C30__shared.active_manifest_carriers',
                    'ADAPTERS_C30__shared.select_manifest_carriers',
                    'ADAPTERS_C30__shared.manifest_inputs',
                    'ADAPTERS_C30__shared.manifest_state_fields',
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
                        'arguments': ['<project-root>', '<control-root>', '<project-manifest-sha256>', '<generation-directory>', '[--ingested-model | --build-model | --model-descriptor-sha256 <hash>]', '[--attest-model]'],
                        'input': 'With --ingested-model, JSON on stdin with rows, has_c9, issues and accepted_model',
                        'output': 'With --ingested-model, JSON with structure, model_descriptor_sha256 and model_diagnostics on stdout; failure JSON with error and model_diagnostics on stderr with nonzero exit. Otherwise, Structure JSON on stdout, wrapped with model_descriptor_sha256 when --attest-model is set',
                        'structure_result': {
                            'record_properties': [
                                'project_manifest_reference', 'project_manifest_digest',
                                'component_ownership', 'component_source_pins',
                                'component_seed_owner', 'component_seed_manifest_reference',
                            ],
                        },
                    },
                    'image_model_stage': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage',
                        'arguments': ['<project-root>', '<control-root>', '<timeout-seconds>', '[<previous-image-id>]'],
                    },
                    'stage_previous_image': {'outcomes': {
                        'accepted': {'must_effect': [('previous_image_selection', 'matched'), ('staged_source_inventory', 'unchanged'), ('previous_image', 'accepted')]},
                        'unavailable': {'forbid_effect': ['previous_image']},
                        'mismatch': {'forbid_effect': ['previous_image']},
                        'inventory_changed': {'forbid_effect': ['previous_image']},
                    }},
                    'image_model_compile': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile',
                    },
                },
                'client': [
                    {'component': 'C45', 'interface': 'previous_image_model_claim_selection'},
                    {'component': 'C53', 'interface': 'admitted_model', 'transport': 'in_process',
                     'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model'},
                ],
            },
            'state': {
                'reads': ['active Project, Component and Component Seed manifests', 'admitted Model claims', 'previous-image claim selection'],
                'writes': ['generated Model package and metadata', 'private Model staging files'],
            },
        },
    ),
)
```
