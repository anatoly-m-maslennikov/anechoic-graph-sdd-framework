"""Named Project selection, lifecycle, and runtime operations."""

from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    runtime_process_boundary as runtime_process_boundary_module,
)
from .artifact_metadata import (
    SETTINGS_PATH,
    atomic_write,
    configured_timezone,
    current_timestamp,
    project_identity,
    repository_root,
)
from .header_yaml import header_scalar, parse_header
from .PROJECT_SUPPORT.PROJECT_SUPPORT__shared import legacy_settings_to_manifest
from .ATOM_LIFECYCLE.NATIVE_LIFECYCLE.NATIVE_LIFECYCLE__shared import (
    NativeDefinitionPin,
    NativeWorkflowDefinitionError,
    bind_native_workflow,
    bind_status_specifications,
    declared_release_entrypoint,
)
from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    ExplicitBlockingRuntimeFailure,
    FailureRecord,
    classify_failure,
    emit_failure_diagnostic,
    operation_error_boundary,
)
from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    ProjectMcpBootstrapError,
    deploy_project_mcp_bootstrap,
)
from .project_root_container import effective_root_container_header
from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    repository_root as runtime_project_root,
)
from .PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared import (
    ProjectSelection,
    _declaration_boundary_proof,
    active_selection,
    bind_selection,
    rebind_selection,
    resolve_project,
)
from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import run_process
from .PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (
    TechnicalDiagnosticLogger,
    make_technical_logger,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import LIFECYCLE_TOOLS
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    ManifestIdentity,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    NativeProjectSelection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    bind_native_runtime,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    discover_native_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    execute_native_lifecycle,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    is_native_control_name,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    mcp_tool_blacklist,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    rebind_native_selection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    report_failure,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)


def indexed_draft_runner():
    """Load the indexed lifecycle path before a worker forks."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
        create_draft as create_draft,
    )
    from .native_lifecycle_cli import run

    return run


__all__ = [
    "ExplicitBlockingRuntimeFailure",
    "FailureRecord",
    "LIFECYCLE_TOOLS",
    "ManifestIdentity",
    "NativeDefinitionPin",
    "NativeProjectSelection",
    "NativeWorkflowDefinitionError",
    "ProjectMcpBootstrapError",
    "ProjectSelection",
    "SETTINGS_PATH",
    "TechnicalDiagnosticLogger",
    "_declaration_boundary_proof",
    "active_selection",
    "atomic_write",
    "bind_native_runtime",
    "bind_selection",
    "bind_native_workflow",
    "bind_status_specifications",
    "classify_failure",
    "configured_timezone",
    "current_timestamp",
    "declared_release_entrypoint",
    "deploy_project_mcp_bootstrap",
    "discover_native_project",
    "emit_failure_diagnostic",
    "execute_native_lifecycle",
    "indexed_draft_runner",
    "is_native_control_name",
    "effective_root_container_header",
    "header_scalar",
    "legacy_settings_to_manifest",
    "make_technical_logger",
    "mcp_tool_blacklist",
    "operation_error_boundary",
    "parse_header",
    "project_identity",
    "rebind_native_selection",
    "rebind_selection",
    "report_failure",
    "repository_root",
    "resolve_native_project",
    "resolve_project",
    "run_process",
    "runtime_process_boundary_module",
    "runtime_project_root",
]
