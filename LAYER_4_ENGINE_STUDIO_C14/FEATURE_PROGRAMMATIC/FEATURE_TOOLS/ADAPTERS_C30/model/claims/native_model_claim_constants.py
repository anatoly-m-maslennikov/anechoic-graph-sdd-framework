"""Constants for native Model claim parsing."""

_DECLARATIONS = {"declare_entity": "entity", "declare_relation": "relation"}


_BUILTINS = {
    "str",
    "int",
    "bool",
    "float",
    "bytes",
    "list",
    "tuple",
    "dict",
    "set",
    "object",
}


_IMPORTS = {
    "anechoic.formal_claims": {
        "declare_entity",
        "declare_relation",
        "Cardinality",
    },
    "datetime": {"date", "datetime", "time", "timedelta"},
    "dataclasses": {"dataclass", "field"},
    "typing": {"Annotated", "ClassVar", "Literal", "Optional"},
    "__future__": {"annotations"},
}


_COUNT_KEYS = {
    "property_occurrence_cardinality",
    "value_cardinality",
    "dependent_property_cardinality",
    "dependent_property_value_cardinality",
    "recursive_dependent_property_cardinality",
    "instance_population_cardinality",
    "targets_per_source",
    "sources_per_target",
}


_ENDPOINT_KEYS = {
    "level",
    "entity_paths",
    "reference_form",
    "dependency",
    "axis",
    "ephemeral",
    "address_form",
}


_ENDPOINT_LEVELS = {
    "model_entities",
    "instances",
    "model_entities_or_instances",
}


_DECLARATION_KEYS = {
    "declare_entity": {
        "entity_name",
        "entity_class",
        "ssot_carrier_path",
        "creation_enabled",
        "instance",
        "instance_check",
        "qualification_property_path",
        "incoming_model_relations",
        "structure_paths",
        "aspect_memberships",
        "entity_kind",
        "identity_properties",
        "field_options",
        "derived_from_properties",
        "constraints_for",
        "relation_name",
        "base_path",
        "value_format",
        "value_cardinality",
        "property_occurrence_cardinality",
        "dependent_property_cardinality",
        "dependent_property_name_format",
        "dependent_property_value_format",
        "dependent_property_value_cardinality",
        "recursive_dependent_property_cardinality",
        "recursive_dependent_property_name_format",
        "recursive_dependent_property_value_format",
        "ordered_dependent_property_roles",
        "allowed_dependent_property_names",
        "ordered_dependent_property_pairs",
        "allowed_values",
        "allowed_relation_names",
        "minimum_value",
        "applies_to_entity_classes",
        "instance_population_cardinality",
        "instance_population_scope",
        "population_entity_path",
        "population_functional_dependencies",
        "population_unique_constraints",
        "axes",
        "allowed_axis_values",
        "fallback_property_name",
        "fallback_value",
        "fallback_chain",
        "maximum_value",
        "required_instance_property_values",
        "instance_property_constraints",
        "model_relation_constraints",
        "instance_relation_constraints",
        "status_order_numbers",
        "applies_to_role",
        "applies_to_forms",
        "status_groups",
        "status_group_names",
        "form_roles",
        "form_content",
        "project_form_content",
    },
    "declare_relation": {
        "relation_name",
        "source_endpoint",
        "target_endpoint",
        "endpoint_pairs",
        "inverse_alias",
        "written_alias",
        "derived_from",
        "reverse_written_alias",
        "targets_per_source",
        "sources_per_target",
        "acyclic",
        "same_immediate_bearer",
        "swap_endpoints",
        "swap_endpoint_cardinalities",
        "axes",
        "inverse_axes",
        "forbidden_status_pairs",
    },
}


_RELATION_CONSTRAINT_KEYS = {
    "target_entity_paths",
    "targets_per_source",
    "sources_per_target",
}


_PROPERTY_CONSTRAINT_KEYS = {"value_cardinality"}
