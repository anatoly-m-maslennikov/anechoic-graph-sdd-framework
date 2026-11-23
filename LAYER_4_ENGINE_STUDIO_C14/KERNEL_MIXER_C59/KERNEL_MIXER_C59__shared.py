"""Named native query types for callers outside the kernel Package."""

from . import header_columns as header_columns
from . import relation_registry as relation_registry_module
from .header_columns import (
    HeaderColumn, HeaderSchema, HeaderSchemaState, _matches_format,
    declared_header_schema, infer_header_schema,
)
from .relation_registry import (
    RegistryCompilation, RegistryContribution, RelationRegistry, _unambiguous_aliases,
    _warn_colliding_uses, compile_registry, compile_relation_registry, is_registry_declaration,
    registry_contribution, registry_from_contributions,
)
from . import public_rows as public_rows
from .audit_tables import TABLES, _declared_filename_issue, collect_issues, create_tables, publish
from .boundary_tables import prepare_boundaries, remove_boundaries, replace_boundaries
from .content_columns import content_columns
from .content_schema import (
    ContentRule,
    ContentSchema,
    DeclarationSource,
    FormalStatement,
    _schema_from_rules,
    _source,
    compile_content_schema,
    content_schema_from_statements,
    declaration_statements,
)
from .declared_header_rules import (
    HeaderRule, compile_header_rules, header_declaration_rules, header_rules_from_statements,
    resolve_header_rules,
)
from .errors import (
    QueryExecutionError,
    WorkbenchUnavailableError,
)
from .relations import (
    ATOM,
    SCOPE,
    _atom_facts,
    _carrier_facts,
    _graph_sources,
    _materialized_atom,
    _materialized_row,
    _outgoing_facts,
    _scope_facts,
    _scope_references,
    _support_facts,
    _support_for_fact,
    materialize,
    materialize_with_registry,
    relation_registry,
)
from . import relations as relations_module
from .native_query_runtime import NativeQueryInputs
from .native_query_rebuild import NativeQueryRebuild
from .native_service_owner import NativeQueryOwner
from .query_schema import public_schema
from .query_store import QueryStore, _connect
from .import_cache import clear_import_sources, read_import_sources, replace_import_sources
from .import_tables import _create_external_imports_view, publish_imports, remove_imports, replace_imports
from .public_rows import SCOPE_FIELDS, atom_fields, insert_public_rows, projected_rows
from .source_inventory import archived, filename_role_matches, group, markdown_paths
from .source_roles import CANONICAL_ROLE_MARKERS, ROLE_MARKERS
from .source_selection import first_reference_rows
from .spec_trace import (
    PILOT, SpecTraceStore, _read_pins, is_trace_path, native_trace_rows, remove_native_traces,
    replace_native_traces,
)
from .state_lint import _report

__all__ = [
    'ATOM', 'ContentRule', 'ContentSchema', 'DeclarationSource', 'FormalStatement',
    'NativeQueryInputs', 'NativeQueryOwner', 'NativeQueryRebuild', 'QueryExecutionError',
    'SCOPE', 'WorkbenchUnavailableError', '_atom_facts', '_carrier_facts', '_graph_sources',
    '_materialized_atom', '_materialized_row', '_outgoing_facts', '_report', '_schema_from_rules',
    '_scope_facts', '_scope_references', '_source', '_support_facts', '_support_for_fact',
    'compile_content_schema', 'content_schema_from_statements', 'declaration_statements',
    'materialize', 'materialize_with_registry', 'prepare_boundaries', 'public_schema',
    'relation_registry', 'remove_boundaries', 'replace_boundaries', 'header_columns',
    'relation_registry_module', 'HeaderColumn', 'HeaderSchema', 'HeaderSchemaState',
    '_matches_format', 'declared_header_schema', 'infer_header_schema', 'RegistryCompilation',
    'RegistryContribution', 'RelationRegistry', '_unambiguous_aliases', '_warn_colliding_uses',
    'compile_registry', 'compile_relation_registry', 'is_registry_declaration',
    'registry_contribution', 'registry_from_contributions',
    'HeaderRule', 'compile_header_rules', 'header_declaration_rules', 'header_rules_from_statements',
    'resolve_header_rules', 'archived', 'filename_role_matches', 'group', 'markdown_paths',
    'CANONICAL_ROLE_MARKERS', 'ROLE_MARKERS', 'first_reference_rows',
    'QueryStore', '_connect',
    'relations_module', 'clear_import_sources', 'read_import_sources', 'replace_import_sources',
    'PILOT', 'SpecTraceStore', '_read_pins', 'is_trace_path', 'native_trace_rows',
    'remove_native_traces', 'replace_native_traces',
    'TABLES', '_declared_filename_issue', 'collect_issues', 'create_tables', 'publish',
    'content_columns', '_create_external_imports_view', 'publish_imports', 'remove_imports', 'replace_imports',
    'public_rows', 'SCOPE_FIELDS', 'atom_fields', 'insert_public_rows', 'projected_rows',
]
