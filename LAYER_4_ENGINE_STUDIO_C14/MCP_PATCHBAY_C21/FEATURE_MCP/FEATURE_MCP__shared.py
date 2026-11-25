"""MCP feature family interface."""

import os
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
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import ExplicitStartupFailure  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import (  # noqa: E402
    ProjectAdmissionError, ProjectBinding, project_admission, select_runtime_project,
)


def beta_runtime_arguments(selection, socket, workbench_storage=None, journal_storage=None):
    args = ["WORKBENCH_BACKEND_beta_C70.runtime", "--socket", str(socket),
            "--project-root", str(selection.root), "--control-root", selection.control_relative.as_posix(),
            "--instance-id", selection.instance_id, "--manifest-sha256", selection.manifest_sha256,
            "--manifest-path", selection.manifest_path.relative_to(selection.root).as_posix(),
            "--project-prefix", selection.project_prefix, "--project-name", selection.project_name]
    runtime = selection.parameters.get("runtime", {})
    workbench = runtime.get("workbench", {})
    profile = "ANECHOIC_RUNTIME_PROFILE" in os.environ
    if not profile:
        storage = workbench.get("storage", workbench_storage or "disk")
        journal = runtime.get("journal", {}).get("storage", journal_storage or "files")
        args += ["--workbench-storage", storage, "--journal-storage", journal]
    public_url = workbench.get("public_url")
    if isinstance(public_url, str) and public_url and "\0" not in public_url:
        args.append(f"--workbench-public-url={public_url}")
    journal_relative = selection.parameters.get("paths", {}).get("journal_root")
    if journal_relative is not None:
        if not isinstance(journal_relative, str):
            raise ValueError("paths.journal_root must be a relative path")
        args += ["--journal-relative", journal_relative]
    if "result_ttl_seconds" in workbench:
        ttl = workbench["result_ttl_seconds"]
        if type(ttl) is not int or ttl <= 0:
            raise ValueError("workbench.result_ttl_seconds must be a positive integer")
        args += ["--result-ttl-seconds", str(ttl)]
    if selection.host_root is not None:
        args += ["--host-root", str(selection.host_root)]
    if workbench.get("import_graph") is not False:
        args.append("--watch-code")
    for name in selection.tool_blacklist:
        args += ["--blacklist", name]
    return args


__all__ = ["ExplicitStartupFailure", "HEALTH_PATH", "MCP_PATH", "ProjectAdmissionError", "ProjectBinding",
           "WORKBENCH_PATH", "beta_runtime_arguments", "project_admission", "select_runtime_project"]
