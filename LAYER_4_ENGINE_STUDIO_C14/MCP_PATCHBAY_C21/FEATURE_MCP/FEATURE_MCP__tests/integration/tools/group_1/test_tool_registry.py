"""Functional registry generation and generic MCP Provider dispatch."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


MCP = Path(__file__).resolve().parents[4]
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    load_active_registry,
)


class MovedRegistryStagingTests(unittest.TestCase):
    def test_checked_in_tool_registry_is_current(self):
        load_active_registry(
            MCP.parents[1]
            / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND",
            MCP.parents[2],
            None,
        )

    def test_staged_compiler_loads_moved_components(self):
        sys.path.insert(0, str(MCP / "docker"))
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
            compile_tool_registry,
        )

        registry = json.loads(
            compile_tool_registry(
                MCP.parents[2], timeout=60, max_output=2_000_000
            )
        )
        self.assertEqual(
            {provider["provider_id"] for provider in registry["providers"]},
            {"workbench", "lifecycle", "release_commands"},
        )
