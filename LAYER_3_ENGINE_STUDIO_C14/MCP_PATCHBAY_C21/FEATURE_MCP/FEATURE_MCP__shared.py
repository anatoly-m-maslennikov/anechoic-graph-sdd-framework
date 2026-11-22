"""MCP feature family interface."""

from pathlib import Path
import sys

_MCP = str(Path(__file__).resolve().parents[2])
if _MCP not in sys.path:
    sys.path.insert(0, _MCP)

from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project  # noqa: E402

__all__ = ["select_runtime_project"]
