"""Entry points for this Adapter package."""

from .atom_reference__pub import (
    is_native_atom_reference as is_native_atom_reference,
    atom_identifier as atom_identifier,
)
from .carrier_body__pub import (
    frontmatter_bounds as frontmatter_bounds,
    source_body as source_body,
)
from .carrier_compat__pub import (
    GROUP_FIELDS as GROUP_FIELDS,
    GROUP_ORDER as GROUP_ORDER,
    ROLE_FIELDS as ROLE_FIELDS,
    canonical_role_name as canonical_role_name,
    carrier_read_view as carrier_read_view,
    equal_values as equal_values,
    header_field_paths as header_field_paths,
    header_path as header_path,
    header_value as header_value,
    is_current_requirement_declaration as is_current_requirement_declaration,
    is_logical_container as is_logical_container,
    matches_carrier_label as matches_carrier_label,
    path_value as path_value,
    project_root_container_view as project_root_container_view,
)
from .carrier_layout__pub import (
    PlacementError as PlacementError,
    admitted_parent as admitted_parent,
    carrier_slug as carrier_slug,
    compile_role_folders as compile_role_folders,
    derive_filename as derive_filename,
    role_folders_from_orders as role_folders_from_orders,
)
from .carrier_read__pub import (
    ParsedCarrier as ParsedCarrier,
    parse_carrier as parse_carrier,
)
from .carrier_syntax__pub import (
    CarrierError as CarrierError,
    UniqueSafeLoader as UniqueSafeLoader,
    check_yaml_resources as check_yaml_resources,
)
from .content_records__pub import (
    content_record_span as content_record_span,
    records_by_path as records_by_path,
    value_excluding_declared_children as value_excluding_declared_children,
)
from .markdown_content__pub import (
    summary_title as summary_title,
    content_key as content_key,
    content_lines as content_lines,
    direct_markdown as direct_markdown,
    formal_claim_fences as formal_claim_fences,
    parse_content as parse_content,
    section_markdown as section_markdown,
    source_markdown as source_markdown,
    unfenced_atx_headings as unfenced_atx_headings,
)
