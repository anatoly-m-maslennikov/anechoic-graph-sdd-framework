"""MCP feature family interface."""

# ruff: noqa: E402

from pathlib import Path
import sys

_MCP = str(Path(__file__).resolve().parents[2])
if _MCP not in sys.path:
    sys.path.insert(0, _MCP)

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    HEALTH_PATH as HEALTH_PATH,
    MCP_PATH as MCP_PATH,
    TOOL_REST_PATH as TOOL_REST_PATH,
    WORKBENCH_PATH as WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import (  # noqa: E402
    HealthObservations,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.health_page import (  # noqa: E402
    render_health_page,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import (  # noqa: E402
    ExplicitStartupFailure,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import (  # noqa: E402
    ProjectAdmissionError,
    ProjectBinding,
    project_admission,
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    native_arguments,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (  # noqa: E402
    runtime_stack,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.\
    runtime_request_context import (  # noqa: E402
    RuntimeRequestContext,
    bind_request_context,
    current_request_context,
)  # fmt: skip


from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import (  # noqa: E402
    BackendClient,
    ToolProtocolError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import (  # noqa: E402
    take_caller_context,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    DirectGateway,
    native_project_gateway,
    native_runtime_gateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    SharedBackendGateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    SharedGatewayRefusal,
    _raise_fault,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    valid_tool_response,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    create_http_app as create_http_app,
    main as http_main,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.server import (  # noqa: E402
    main as server_main,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    create_shared_http_app as create_shared_http_app,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    public_tool,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    Invocation,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as workbench_routes,
)


__all__ = [
    "BackendClient",
    "DirectGateway",
    "ExplicitStartupFailure",
    "HEALTH_PATH",
    "HealthObservations",
    "Invocation",
    "MCP_PATH",
    "ProjectAdmissionError",
    "ProjectBinding",
    "RuntimeRequestContext",
    "SharedBackendGateway",
    "SharedGatewayRefusal",
    "TOOL_REST_PATH",
    "ToolProtocolError",
    "WORKBENCH_PATH",
    "_raise_fault",
    "bind_request_context",
    "create_http_app",
    "create_shared_http_app",
    "current_request_context",
    "http_main",
    "native_arguments",
    "native_project_gateway",
    "native_runtime_gateway",
    "project_admission",
    "public_tool",
    "render_health_page",
    "runtime_stack",
    "select_runtime_project",
    "server_main",
    "take_caller_context",
    "valid_tool_response",
    "workbench_routes",
]
