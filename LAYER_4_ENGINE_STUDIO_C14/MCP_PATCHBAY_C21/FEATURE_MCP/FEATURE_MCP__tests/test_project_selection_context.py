"""Admitted Project selection arguments at the entrypoint boundary."""

# ruff: noqa: E402
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    http_main,
    runtime_stack,
    select_runtime_project,
)
from . import test_native_host_launcher as host_fixture


class ProjectContextTests(unittest.TestCase):
    def setUp(self):
        host_fixture.NativeHostLauncherTests.setUp(self)
        self.selections = [select_runtime_project(self.root)]

    def test_docker_entrypoint_forwards_only_admitted_selection_arguments(
        self,
    ):
        import importlib.util

        path = MCP / "docker/entrypoint.py"
        specification = importlib.util.spec_from_file_location(
            "project_selection_entrypoint", path
        )
        entrypoint = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(entrypoint)
        selection = self.selections[0]
        values = {
            "ANECHOIC_RUNTIME_STACK": "current",
            "ANECHOIC_CONTROL_ROOT": selection.control_relative.as_posix(),
            "ANECHOIC_PROJECT_INSTANCE_ID": selection.instance_id,
            "ANECHOIC_HOST_PROJECT_ROOT": str(selection.host_root),
            "ANECHOIC_MCP_HTTP_SECRET_TOKEN": "private",
        }
        with (
            patch.object(sys, "argv", ["entrypoint", "mcp-http"]),
            patch.dict(os.environ, values),
            patch.object(os, "execve") as execute,
        ):
            entrypoint.main()
        arguments = execute.call_args.args[1]
        self.assertEqual(
            selection.control_relative.as_posix(),
            arguments[arguments.index("--control-root") + 1],
        )
        self.assertEqual(
            selection.instance_id,
            arguments[arguments.index("--instance-id") + 1],
        )
        self.assertNotIn("private", arguments)

    def test_http_refuses_a_retired_runtime_stack_before_launch(self):
        runtime_stack.cache_clear()
        self.addCleanup(runtime_stack.cache_clear)
        with (
            patch.dict(os.environ, {"ANECHOIC_RUNTIME_STACK": "beta_next"}),
            patch("uvicorn.run") as serve,
        ):
            self.assertNotEqual(0, http_main(["--project-root", str(self.root)]))
        serve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
