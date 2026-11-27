"""Use the MCP service's fixed routes without importing its server runtime."""

from __future__ import annotations


def _canonical_paths() -> tuple[str, str]:
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
        HEALTH_PATH,
        MCP_PATH,
    )

    return MCP_PATH, HEALTH_PATH


MCP_PATH, HEALTH_PATH = _canonical_paths()

__all__ = ["HEALTH_PATH", "MCP_PATH"]
