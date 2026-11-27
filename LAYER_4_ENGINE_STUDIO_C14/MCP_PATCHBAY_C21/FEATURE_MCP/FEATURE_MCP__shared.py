"""MCP feature family interface."""

from pathlib import Path
import sys

_MCP = str(Path(__file__).resolve().parents[2])
if _MCP not in sys.path:
    sys.path.insert(0, _MCP)

from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import (  # noqa: E402
    HEALTH_PATH as HEALTH_PATH,
    MCP_PATH as MCP_PATH,
    WORKBENCH_PATH as WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import HealthObservations  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.health_page import render_health_page  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import (  # noqa: E402
    ExplicitStartupFailure,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import (  # noqa: E402
    ProjectAdmissionError,
    ProjectBinding,
    project_admission,
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import native_arguments  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import (  # noqa: E402
    beta_runtime_arguments,
    runtime_stack,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import (  # noqa: E402
    RuntimeRequestContext,
    bind_request_context,
    current_request_context,
)


from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import (  # noqa: E402
    BackendClient,
    ToolProtocolError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import (  # noqa: E402
    DirectGateway,
    native_project_gateway,
    native_runtime_gateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend import (  # noqa: E402
    SharedBackendGateway,
    SharedGatewayRefusal,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import (  # noqa: E402
    create_app as create_http_app,
    main as http_main,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.server import main as server_main  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server import (  # noqa: E402
    create_app as create_shared_http_app,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web import (  # noqa: E402
    routes as workbench_routes,
)


__all__ = [
    "BackendClient",
    "DirectGateway",
    "ExplicitStartupFailure",
    "HEALTH_PATH",
    "HealthObservations",
    "MCP_PATH",
    "ProjectAdmissionError",
    "ProjectBinding",
    "RuntimeRequestContext",
    "SharedBackendGateway",
    "SharedGatewayRefusal",
    "ToolProtocolError",
    "WORKBENCH_PATH",
    "beta_runtime_arguments",
    "bind_request_context",
    "create_http_app",
    "create_shared_http_app",
    "current_request_context",
    "http_main",
    "native_arguments",
    "native_project_gateway",
    "native_runtime_gateway",
    "project_admission",
    "render_health_page",
    "runtime_stack",
    "select_runtime_project",
    "server_main",
    "workbench_routes",
]
