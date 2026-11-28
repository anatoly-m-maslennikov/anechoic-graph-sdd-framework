---
atom_family: SPEC
atom_id: AN-S-3065
container:
  component: C51
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 42
  updated_at: "2026-11-28T15:06:14+00:00"
---

## Summary

Declare FORMAL_MODEL_GENERATOR

## Purpose

Compile and stage a Project Model and validate its Structure for callers.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C50',
    name='FORMAL_MODEL_GENERATOR',
    lens_whitelist=['DES', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [
                      'manifest_compiler_CS1.ingestion._package__shared.compile_ingested_cli','PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared.resolve_native_project', 'PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared.resolve_project', 'carriers.concern.continuant_concern__pub.CONTINUANT_LENS', 'carriers.concern.continuant_concern__pub.continuant_model_subject', 'carriers.concern.continuant_concern__pub.implicit_continuant_node', 'carriers.concern.continuant_concern__pub.model_node_location', 'carriers.concern.continuant_concern__pub.validate_continuant_variant', 'carriers.content.atom_reference__pub.derive_atom_ref', 'carriers.content.carrier_read__pub.parse_carrier', 'model.cardinality__pub.cardinality_bounds', 'model.model_ontology_path__pub.find_ontology_component', 'model.model_ontology_path__pub.is_ontology_model_source', 'model.model_ontology_path__pub.ontology_component_path', 'model.python.dataclass_field_contract__pub.validate_field_contracts', 'model.relation_declaration_catalog__pub.build_relation_declaration_catalog', 'sources.sources__shared.mark_startup_timing', 'structure.components.component_seed_manifest__pub.read_component_seed_manifest', 'structure.components.components__shared.NODE_LINK_PREFIX', 'structure.components.components__shared.parse_typed_manifest_node', 'manifest_compiler_CS1.lean._package__shared.render_atom_header_lean', 'manifest_compiler_CS1.lean._package__shared.verify_model_lean', 'manifest_compiler_CS1.typed._package__shared._endpoints', 'manifest_compiler_CS1.typed._package__shared._field_assignments', 'manifest_compiler_CS1.typed._package__shared._parse_field_body', 'manifest_compiler_CS1.typed._package__shared._reference', 'manifest_compiler_CS1.typed._package__shared._references', 'manifest_compiler_CS1.typed._package__shared._lower_axis', 'manifest_compiler_CS1.typed._package__shared._lower_property_value', 'manifest_compiler_CS1.typed._package__shared.typed_addresses', 'manifest_compiler_CS1.typed._package__shared._model_record', 'manifest_compiler_CS1.typed._package__shared.lower_typed_node',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._add_unambiguous_addresses',
                      'assembly._manifest_property_selection._merge_overrides',
                      'assembly._manifest_property_selection._property_fields',
                      'assembly._manifest_property_validation._PATH',
                      'assembly._manifest_property_validation._check_property_fields',
                      'assembly._manifest_property_validation._override_target',
                      'assembly._manifest_property_validation._owner',
                      'assembly._manifest_property_validation._property_groups',
                      'assembly._manifest_property_validation._record_group_child',
                      'assembly._manifest_property_validation._relative_property_path',
                      'assembly._manifest_property_validation._subclass',
                      'assembly._manifest_property_validation._validate_identities',
                      'assembly.model_class_assembly.model_module_name',
                      'manifest_compiler_CS1.compiler.write_model_records',
                      'manifest_compiler_CS1.lean.model_lean.render_atom_header_lean',
                      'manifest_compiler_CS1.typed.typed_node_lowering.lower_typed_node',
                      'manifest_compiler_CS1.typed_property_relation_lowering.typed_property_subject',
                      'manifest_property_fields.assemble_manifest_fields',
                      'model_declaration_sources._check_relation_references',
                      'model_declaration_sources._merge_constraint_claims',
                      'model_declaration_sources.select_model_claims',
                      'model_node_axes._inherit_node_axes',
                      'native.native_manifest_model.admit_active_model_records',
                      'native.native_manifest_model.compile_native_bindings',
                      'native.native_manifest_model.load_compiled_model',
                      'native.native_manifest_model.reviewed_model_records','admission.bound_native_model.BoundNativeModel', 'admission.bound_native_model.is_reviewed_claim', 'admission.bound_native_model.normalize_reviewed_claim', 'assembly._manifest_property_validation._field_name', 'assembly.model_class_assembly.assemble_model_classes', 'assembly.model_class_assembly.assemble_model_modules', 'assembly.model_class_assembly.build_model_class_source', 'native.native_manifest_model', 'native.native_manifest_model.load_native_model',
                      'manifest_compiler_CS1.active_model_sources',
                      'manifest_compiler_CS1.active_model_sources._collect_node_metadata',
                      'manifest_compiler_CS1.active_model_sources.compile_active_model_rows',
                      'manifest_compiler_CS1.image_model_stage',
                      'manifest_compiler_CS1.model_ingestion',
                      'manifest_compiler_CS1.typed_node_constraints.lower_node_constraints',
                      'manifest_compiler_CS1.typed_node_lowering.lower_typed_node',
                      'manifest_compiler_CS1.typed_property_relation_lowering.declared_relation_names',
                      'manifest_compiler_CS1.typed_property_relation_lowering.lower_typed_fields',
                      'manifest_property_fields._index_classes',
                      'model_constraint_claims._constraint_owners',
                      'model_constraint_claims._merge_constraint_claims',
                      'model_declaration_sources._check_node_axes',
                      'native_manifest_model._NativeModel',
                      'manifest_compiler_CS1__shared.bounded_run',
                      'manifest_compiler_CS1__shared.previous_claims',
                      'manifest_compiler_CS1__shared.stage_model',
                      'manifest_compiler_CS1__shared.read_active_model_sources',
                      'manifest_compiler_CS1__shared.render_atom_header_lean',
                      'manifest_compiler_CS1__shared.verify_model_lean',
                      'manifest_compiler_CS1__shared.compile_ingested_cli',
                      'manifest_compiler_CS1__shared.write_model',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_manifest_property_bearers',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_relation_references',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_node_axes',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._field_name',
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.relation_axis_values',
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
                      'FEATURE_MODEL_VALIDATION__shared.BoundNativeModel',
                      'FEATURE_MODEL_VALIDATION__shared.validate_model_instance',
                      'FEATURE_MODEL_VALIDATION__shared.is_reviewed_claim',
                      'ADAPTERS_C30__shared.NODE_LINK_PREFIX',
                      'ADAPTERS_C30__shared.parse_typed_manifest_node',
                      'model_ontology_path__pub.is_ontology_model_source',
                      'model_ontology_path__pub.ontology_component_path',
                      'model_ontology_path__pub.find_ontology_component',
                      'ATOM_LIFECYCLE.drafts.native_draft_guards._validate_c9_typed_manifest',
                      'ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared.InputError',
                      'native_model_selector',
                      'component_seed_manifest__pub.read_component_seed_manifest',
                      'FEATURE_MODEL_VALIDATION__shared.validate_relation_endpoint_levels',
                      'model_relation_validation.validate_model_relations',
                      'continuant_concern__pub.CONTINUANT_LENS',
                      'continuant_concern__pub.continuant_model_subject',
                      'continuant_concern__pub.implicit_continuant_node',
                      'continuant_concern__pub.model_node_location',
                      'continuant_concern__pub.validate_continuant_variant',
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
                      'dataclass_field_contract__pub.validate_field_contracts',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.resolve_model_claim_reference',
                      'FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared.native_model_claim_linter',
                      'FEATURE_FORMAL_MODEL_ENGINE.native_model_lint__pub',
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
                      'ADAPTERS_C30__shared.active_manifest_carriers',
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
                      'ADAPTERS_C30__shared.profile_evidence'],
          'exports': {'manifest_compiler_CS1.ingestion._package__shared.compile_ingested_cli': {'private': ['C75', 'CS1']},
                      'manifest_compiler_CS1.lean._package__shared.render_atom_header_lean': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1']}, 'manifest_compiler_CS1.lean._package__shared.verify_model_lean': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1']}, 'manifest_compiler_CS1.typed._package__shared._endpoints': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._field_assignments': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/drafts', 'CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._parse_field_body': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._reference': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._references': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._lower_axis': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._lower_property_value': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared.typed_addresses': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared._model_record': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']}, 'manifest_compiler_CS1.typed._package__shared.lower_typed_node': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']},
                      'manifest_compiler_CS1.compiler.write_model_records': {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/ingestion']},
                      'manifest_compiler_CS1.lean.model_lean.render_atom_header_lean': {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'manifest_compiler_CS1.typed.typed_node_lowering.lower_typed_node': {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields']},
                      'manifest_compiler_CS1.typed_property_relation_lowering.typed_property_subject': {"private": ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active']},'native.native_manifest_model.reviewed_model_records': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1']}, 'native.native_manifest_model.load_compiled_model': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1']}, 'native.native_manifest_model.compile_native_bindings': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']}, 'native.native_manifest_model.admit_active_model_records': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']}, 'native.native_manifest_model': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']}, 'native.native_manifest_model.load_native_model': {'private': ['C19', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests']}, 'assembly._manifest_property_selection._property_fields': {'private': ['C50']}, 'assembly._manifest_property_selection._merge_overrides': {'private': ['C50']}, 'assembly._manifest_property_validation._PATH': {'private': ['C50']}, 'assembly._manifest_property_validation._field_name': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/typed', 'C50']}, 'assembly._manifest_property_validation._owner': {'private': ['C50']}, 'assembly._manifest_property_validation._subclass': {'private': ['C50']}, 'assembly._manifest_property_validation._relative_property_path': {'private': ['C50']}, 'assembly._manifest_property_validation._property_groups': {'private': ['C50']}, 'assembly._manifest_property_validation._override_target': {'private': ['C50']}, 'assembly._manifest_property_validation._check_property_fields': {'private': ['C50']}, 'assembly._manifest_property_validation._record_group_child': {'private': ['C50']}, 'assembly._manifest_property_validation._validate_identities': {'private': ['C50']}, 'model_node_axes._inherit_node_axes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'model_declaration_sources._check_relation_references': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'model_declaration_sources._merge_constraint_claims': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'native._package__shared.admit_active_model_records': {'private': ['C50']}, 'native._package__shared.compile_native_bindings': {'private': ['C50']}, 'native._package__shared.load_compiled_model': {'private': ['C50']}, 'native._package__shared.reviewed_model_records': {'private': ['C50']}, 'native._package__shared.native_manifest_model': {'private': ['C50']}, 'native._package__shared.load_native_model': {'private': ['C19', 'C50', 'C75']}, 'assembly.model_class_assembly.assemble_model_classes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'C50', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'assembly.model_class_assembly.assemble_model_modules': {'private': ['C50', 'CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'assembly.model_class_assembly.build_model_class_source': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'C50', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'assembly.model_class_assembly.model_module_name': {'private': ['C50', 'CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/native']}, 'manifest_property_fields.assemble_manifest_fields': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/assembly']}, 'model_declaration_sources.select_model_claims': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/assembly']},
                      'manifest_property_fields._index_classes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'model_constraint_claims._constraint_owners': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'model_constraint_claims._merge_constraint_claims': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/sources', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/ingestion']},
                      'model_declaration_sources._check_node_axes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/sources', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/ingestion']},
                      'native_manifest_model._NativeModel': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/sources', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/typed_fields', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/ingestion']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_node_axes': {'private': ['CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._field_name': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/typed', 'CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.relation_axis_values': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/lean', 'CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._add_unambiguous_addresses': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/lean', 'CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_manifest_property_bearers': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._check_relation_references': {'private': ['CS1', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._class_property_aliases': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/lean', 'CS1',
                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._merge_constraint_claims': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._native_claim': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active', 'CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared._native_claim_text': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/active', 'CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.admit_active_model_records': {'private': ['CS1',
                                                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.assemble_model_classes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.assemble_model_modules': {'private': ['CS1',
                                                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.build_model_class_source': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.compile_native_bindings': {'private': ['CS1',
                                                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.load_compiled_model': {'private': ['CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.load_native_model': {'private': ['C75', 'CS1',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties', 'C19']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.model_module_name': {'private': ['CS1']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.native_manifest_model': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.reviewed_model_records': {'private': ['CS1',
                                                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/manifest_compiler_CS1/manifest_compiler_CS1__tests/functional']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.select_model_claims': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']},
                      'FEATURE_FORMAL_MODEL_GENERATOR__shared.select_model_declarations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/assembly', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/declarations', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_FORMAL_MODEL_GENERATOR/FEATURE_FORMAL_MODEL_GENERATOR__tests/properties']}}},
 'io': {'server': {'manifest_compile': {'transport': 'in_process',
                                        'entry': 'manifest_compiler_CS1__shared.compile_ingested_cli'},
                   'standalone_model_generate': {'transport': 'cli',
                                                 'runner': 'managed_python',
                                                 'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.generate_model',
                                                 'arguments': ['--project-root',
                                                               '<project-root>',
                                                               '--output',
                                                               '<python-file>']},
                   'image_model_stage': {'transport': 'cli',
                                         'runner': 'managed_python',
                                         'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage',
                                         'arguments': ['<project-root>',
                                                       '<control-root>',
                                                       '<timeout-seconds>',
                                                       '[<previous-image-id>]']},
                   'image_model_compile': {'transport': 'cli',
                                           'runner': 'managed_python',
                                           'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile'}},
        'client': [{'component': 'C45',
                    'interface': 'previous_image_model_claim_selection'},
                   {'component': 'C93', 'interface': 'compile_project_structure'},
                   {'component': 'C53', 'interface': 'admitted_model'}]},
 'state': {'reads': ['selected Project Manifest and its admission pin',
                     'pinned Model rows and the accepted compiled Model',
                     'previous-image claim selection'],
           'writes': ['generated Model package and metadata',
                      'private Model staging files']}}
```

## Component Contract

### Stage a Model for image admission

#### Guarantee

Managed Model builds receive pinned Model rows from the Project Spec snapshot.
File-based Model source discovery applies to offline builds.

When a Project C9 is staged, require the supplied previous image to select the same Claims. Reject an unavailable image or changed source inventory.

Without Project C9, use the bundled reviewed Claims. If a previous image is supplied, check that it is available.

### Stage an ingested Model and Structure

#### Guarantee

Compile the supplied Model rows and stage the descriptor. Validate it with the Structure compiler supplied by C75. Return the descriptor digest and Model diagnostics.
Reuse a loadable Model when its input fingerprint matches and the Operator has requested no Model rebuild.

Compile permitted Project Config templates, statuses, allowed values,
and defaults with the Model rows. Stage a usable fallback with diagnostics
if candidate compilation or admission fails.

The bootstrap Model used to ingest inputs has a separate role from the
selected reused, compiled, or fallback Model. They may have the same
fingerprint. Open the selected staged descriptor
with C53 and compile Structure with that Model using the supplied compiler.
For pinned snapshot rows, the compiler is C93 `compile_pinned_structure`
under AN-S-5018@8. Return the selected Model fingerprint and staged
descriptor digest with the Structure.

For comparison, observe `model_sha256` and `descriptor_sha256` at each
branch's selected Model and its C53 opening. Observe `model_sha256` at C93
Structure and in the returned Structure, as `structure.model_sha256`. At opening,
read the yielded Model fingerprint and the digest of the verified descriptor
bytes. Compare the staged digest with returned `model_descriptor_sha256`.
Missing independent observations leave identity unresolved.

```python trace
declare_trace_contract(
    action='manifest_compile',
    interface='manifest_compile',
    transport='in_process',
    effects={
        'reuse': ('C50.compiled_model_asset', 'validated'),
        'compile': ('C50.model_generation', 'staged'),
        'fallback': ('C50.model_generation', 'restored'),
        'diagnostics': ('C50.model_diagnostics', 'recorded'),
        'open': ('C53.admitted_model', 'opened'),
        'structure': ('C93.structure_snapshot', 'ready'),
    },
    cases={
        'reused': {
            'must_effect': ('reuse', 'open', 'structure'),
            'must_precede': (('reuse', 'open'), ('open', 'structure')),
            'same_values': (
                (('asset_validated', 'model_sha256'), ('reuse_model_opened', 'model_sha256')),
                (('reuse_model_opened', 'model_sha256'), ('structure_ready', 'model_sha256')),
                (('structure_ready', 'model_sha256'), ('returned', 'model_sha256')),
                (('asset_validated', 'descriptor_sha256'), ('reuse_model_opened', 'descriptor_sha256')),
                (('reuse_model_opened', 'descriptor_sha256'), ('returned', 'model_descriptor_sha256')),
            ),
            'value_types': {('asset_validated', 'model_sha256'): 'nonempty_string',
                            ('asset_validated', 'descriptor_sha256'): 'nonempty_string'},
            'forbid_effect': ('C50.model_generation',),
        },
        'compiled': {
            'must_effect': ('compile', 'open', 'structure'),
            'must_precede': (('compile', 'open'), ('open', 'structure')),
            'same_values': (
                (('candidate_staged', 'model_sha256'), ('compiled_model_opened', 'model_sha256')),
                (('compiled_model_opened', 'model_sha256'), ('structure_ready', 'model_sha256')),
                (('structure_ready', 'model_sha256'), ('returned', 'model_sha256')),
                (('candidate_staged', 'descriptor_sha256'), ('compiled_model_opened', 'descriptor_sha256')),
                (('compiled_model_opened', 'descriptor_sha256'), ('returned', 'model_descriptor_sha256')),
            ),
            'value_types': {('candidate_staged', 'model_sha256'): 'nonempty_string',
                            ('candidate_staged', 'descriptor_sha256'): 'nonempty_string'},
        },
        'fallback': {
            'must_effect': ('diagnostics', 'fallback', 'open', 'structure'),
            'must_precede': (('diagnostics', 'fallback'), ('fallback', 'open'), ('open', 'structure')),
            'same_values': (
                (('fallback_selected', 'model_sha256'), ('fallback_model_opened', 'model_sha256')),
                (('fallback_model_opened', 'model_sha256'), ('structure_ready', 'model_sha256')),
                (('structure_ready', 'model_sha256'), ('returned', 'model_sha256')),
                (('fallback_selected', 'descriptor_sha256'), ('fallback_model_opened', 'descriptor_sha256')),
                (('fallback_model_opened', 'descriptor_sha256'), ('returned', 'model_descriptor_sha256')),
            ),
            'value_types': {('fallback_selected', 'model_sha256'): 'nonempty_string',
                            ('fallback_selected', 'descriptor_sha256'): 'nonempty_string'},
        },
        'failed': {},
    },
)
```
