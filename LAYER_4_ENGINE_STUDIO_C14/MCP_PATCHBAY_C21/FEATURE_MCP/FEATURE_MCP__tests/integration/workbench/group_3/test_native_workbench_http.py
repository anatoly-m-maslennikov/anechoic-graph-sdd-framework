"""The existing Workbench HTTP contract uses the native Project store."""

import asyncio
import json as json
import sys as sys
from dataclasses import replace
from pathlib import Path as Path
import shlex as shlex
import unittest
from unittest.mock import patch as patch

import httpx2 as httpx2
from mcp import types as types
from starlette.applications import Starlette as Starlette

from ...query.group_1 import test_native_query_stdio as fixture
from ..group_1.native_workbench_http_cases import NativeWorkbenchStateCases
from ..group_2.native_workbench_lifecycle_cases import (
    NativeWorkbenchLifecycleCases,
)
from ..group_1.native_workbench_release_http_cases import (
    NativeWorkbenchReleaseHttpCases,
)
from ....native_query_test_support import (
    create_native_gateway as create_native_gateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project as startup_selection,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


class NativeWorkbenchHttpTests(
    NativeWorkbenchStateCases,
    NativeWorkbenchLifecycleCases,
    NativeWorkbenchReleaseHttpCases,
    unittest.IsolatedAsyncioTestCase,
):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write

    async def test_startup_rebinds_native_identity(self):
        manifest = self.root / fixture.CONTROL / fixture.MANIFEST
        manifest.write_text(
            manifest.read_text().replace(
                "component: C0\n", "component: C00\n", 1
            )
        )
        selection = await asyncio.to_thread(startup_selection, self.root)
        rebound = await asyncio.to_thread(
            startup_selection,
            self.root,
            instance_id=selection.instance_id,
            host_root=self.root,
        )
        self.assertEqual(replace(selection, host_root=self.root), rebound)
        with self.assertRaises(ValueError):
            await asyncio.to_thread(
                startup_selection, self.root, host_root=self.root
            )
        with self.assertRaises(ValueError):
            await asyncio.to_thread(
                startup_selection,
                self.root,
                instance_id="0" * 64,
                host_root=self.root,
            )

    def _release_claim(
        self,
        operation,
        *,
        status="active",
        entrypoint=None,
        atom_id=None,
        body=None,
    ):
        atom_id = atom_id or (
            "AN-P-058" if operation == "local" else "AN-P-049"
        )
        entrypoint = entrypoint or f"release scripts/{operation}.py"
        if body is None:
            body = (
                f"## Claim\n\n### Formal Claim\n\n```python\n"
                f"release_command(operation={operation!r}, entrypoint={entrypoint!r})\n```\n"
            )
        self._write(
            f"__PROJECT_CONFIG/{atom_id}-WORKFLOW--{operation}.md",
            atom_id,
            status,
            1,
            template="workflow",
            body=body,
        )
        script = self.root / entrypoint
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("# fixture\n", encoding="utf-8")
        return (
            self.root
            / fixture.CONTROL
            / f"__PROJECT_CONFIG/{atom_id}-WORKFLOW--{operation}.md"
        )


if __name__ == "__main__":
    unittest.main()
