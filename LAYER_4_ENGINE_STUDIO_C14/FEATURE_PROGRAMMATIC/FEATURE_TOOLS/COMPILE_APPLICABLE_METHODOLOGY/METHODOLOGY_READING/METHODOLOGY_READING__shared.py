"""Source reading primitives for the Methodology compiler."""

from .methodology_candidate import (
    Candidate as Candidate,
    DEFAULT_CONTROL_ROOT as DEFAULT_CONTROL_ROOT,
    OUTPUT_RELATIVE as OUTPUT_RELATIVE,
)
from .methodology_conflicts import (
    candidate_sort_key as candidate_sort_key,
    detect_conflicts as detect_conflicts,
    frontier_digest as frontier_digest,
    sha256_bytes as sha256_bytes,
)
from .methodology_paths_settings import (
    DEFAULT_SETTINGS_NAME as DEFAULT_SETTINGS_NAME,
    INSTANCE_SETTINGS_RELATIVE as INSTANCE_SETTINGS_RELATIVE,
    _extension_records as _extension_records,
    extension_selections as extension_selections,
    framework_settings as framework_settings,
    framework_settings_carriers as framework_settings_carriers,
    parse_toml as parse_toml,
    repo_relative as repo_relative,
    safe_framework_settings_carrier as safe_framework_settings_carrier,
)
from .methodology_paths_sources import (
    LAYERS as LAYERS,
    MethodologyPaths as MethodologyPaths,
    SOURCE_RELATIVE as SOURCE_RELATIVE,
    _methodology_places as _methodology_places,
    _methodology_source_unit as _methodology_source_unit,
    _source_layer_authorities as _source_layer_authorities,
    configured_control_root as configured_control_root,
    declaration_source_pins as declaration_source_pins,
    source_layer_paths as source_layer_paths,
)
from .methodology_source_parsing import (
    CompileError as CompileError,
    definition_subject as definition_subject,
    derive_atom_id as derive_atom_id,
    relation_targets as relation_targets,
    relations_digest as relations_digest,
    split_frontmatter as split_frontmatter,
    top_scalar as top_scalar,
)
