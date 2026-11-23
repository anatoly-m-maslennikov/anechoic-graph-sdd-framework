"""Named Project selection, lifecycle, and runtime operations."""

from . import runtime_process_boundary as runtime_process_boundary_module
from .artifact_metadata import (
    SETTINGS_PATH, atomic_write, configured_timezone, current_timestamp, project_identity, repository_root,
)
from .operation_error_boundary import (
    ExplicitBlockingRuntimeFailure, FailureRecord, classify_failure, emit_failure_diagnostic, operation_error_boundary,
)
from .project_runtime import repository_root as runtime_project_root
from .project_selection import (
    ProjectSelection, _declaration_boundary_proof, active_selection, bind_selection, rebind_selection, resolve_project,
)
from .runtime_process_boundary import run_process
from .technical_diagnostics import TechnicalDiagnosticLogger, make_technical_logger
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle import LIFECYCLE_TOOLS
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import ManifestIdentity
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import NativeProjectSelection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_runtime import bind_native_runtime
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_workflow_definition import declared_release_entrypoint
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import discover_native_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle import execute_native_lifecycle
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import is_native_control_name
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_settings_schema import mcp_tool_blacklist
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import rebind_native_selection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.runtime_failure_diagnostics import report_failure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import resolve_native_project


def indexed_draft_runner():
    """Load the indexed lifecycle path before a worker forks."""
    from .ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft  # noqa: F401
    from .native_lifecycle_cli import run
    return run


__all__ = [
    "ExplicitBlockingRuntimeFailure", "FailureRecord", "LIFECYCLE_TOOLS", "ManifestIdentity",
    "NativeProjectSelection", "ProjectSelection", "SETTINGS_PATH", "TechnicalDiagnosticLogger",
    "_declaration_boundary_proof", "active_selection", "atomic_write", "bind_native_runtime", "bind_selection",
    "classify_failure", "configured_timezone", "current_timestamp", "declared_release_entrypoint",
    "discover_native_project", "emit_failure_diagnostic", "execute_native_lifecycle", "indexed_draft_runner", "is_native_control_name",
    "make_technical_logger", "mcp_tool_blacklist", "operation_error_boundary", "project_identity",
    "rebind_native_selection", "rebind_selection", "report_failure", "repository_root", "resolve_native_project",
    "resolve_project", "run_process", "runtime_process_boundary_module", "runtime_project_root",
]
