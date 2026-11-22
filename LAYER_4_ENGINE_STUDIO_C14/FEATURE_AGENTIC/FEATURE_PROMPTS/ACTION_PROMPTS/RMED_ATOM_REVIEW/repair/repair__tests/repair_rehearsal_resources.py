"""Synthetic resource data used by the repair rehearsal fixture."""

PROJECT_STRUCTURE = """schema_version = 1

[[scope_units]]
scope_unit_name = "SYNTHETIC_ROOT"
parent = "PROJECT"
scope_unit_type = "Unordered"
scope_unit_label = "Synthetic rehearsal root"
structural_level = 1
navigational_order_number = 1
authority_path = ".anechoic_synthetic_project/000_ANECHOIC_framework/01_SYNTHETIC_ROOT"
delivery_path = "synthetic/repair-rehearsal"
authority_mode = "strict"

[[scope_units]]
scope_unit_name = "SYNTHETIC_MIDDLE"
parent = "SYNTHETIC_ROOT"
scope_unit_type = "Ordered"
scope_unit_label = "Synthetic rehearsal middle"
structural_level = 2
local_order = 1
navigational_order_number = 2
authority_path = ".anechoic_synthetic_project/000_ANECHOIC_framework/02_SYNTHETIC_MIDDLE"
delivery_path = "synthetic/repair-rehearsal"
authority_mode = "strict"

[[scope_units]]
scope_unit_name = "SYNTHETIC"
parent = "SYNTHETIC_MIDDLE"
scope_unit_type = "Ordered"
scope_unit_label = "Synthetic rehearsal candidate scope"
structural_level = 3
local_order = 1
navigational_order_number = 3
authority_path = ".anechoic_synthetic_project/000_ANECHOIC_framework/03_SYNTHETIC"
delivery_path = "synthetic/repair-rehearsal"
authority_mode = "strict"
"""

PROJECT_SETTINGS = """[project]
name = "synthetic_project"

[artifacts.identity]
project_prefix = "SYN"
"""

OPERATOR_REGISTRY = """[[operators]]
name = "Synthetic Fixture Operator"
role = "fixture reviewer"
"""

FRAMEWORK_SETTINGS = """[confidence]
necessary_information_threshold_percent = 99
semantic_resolution_threshold_percent = 99

[authority_modes]
default = "strict"

[interaction]
reporting_mode = "silent"

[artifacts]
creation_strictness = "medium"

[implementation]
retry_limit = 0

[atom_validation]
max_candidates = 4
max_file_bytes = 1048576
max_total_read_bytes = 4194304
timeout_seconds = 60
max_findings = 100

[rmed_review]
max_atoms = 4
target_minutes = 10
"""

DEFAULT_SETTINGS = """[confidence]
necessary_information_threshold_percent = 99
semantic_resolution_threshold_percent = 99

[authority_modes]
default = "strict"

[interaction]
reporting_mode = "silent"

[artifacts]
creation_strictness = "medium"

[implementation]
retry_limit = 0

[atom_validation]
max_candidates = 4
max_file_bytes = 1048576
max_total_read_bytes = 4194304
timeout_seconds = 60
max_findings = 100

[rmed_review]
max_atoms = 4
target_minutes = 10
"""
