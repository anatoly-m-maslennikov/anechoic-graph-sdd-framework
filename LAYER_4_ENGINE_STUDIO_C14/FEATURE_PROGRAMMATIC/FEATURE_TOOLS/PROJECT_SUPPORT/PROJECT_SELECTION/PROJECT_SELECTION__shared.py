"""Project selection and discovery."""

from .native_project_selection import (
    ManifestIdentity as ManifestIdentity,
    NativeProjectSelection as NativeProjectSelection,
    discover_native_project as discover_native_project,
    is_native_control_name as is_native_control_name,
    rebind_native_selection as rebind_native_selection,
    resolve_native_project as resolve_native_project,
)
from .project_selection import (
    ProjectSelection as ProjectSelection,
    _declaration_boundary_proof as _declaration_boundary_proof,
    _instance_id as _instance_id,
    _project_root as _project_root,
    active_selection as active_selection,
    bind_selection as bind_selection,
    rebind_selection as rebind_selection,
    resolve_project as resolve_project,
)
