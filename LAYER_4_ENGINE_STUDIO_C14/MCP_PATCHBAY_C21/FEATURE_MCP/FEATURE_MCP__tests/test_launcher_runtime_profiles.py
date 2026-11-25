"""Launcher defaults leave explicit runtime settings and project bindings intact."""

from contextlib import nullcontext
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from MCP_PATCHBAY_C21.FEATURE_MCP import host_http, server
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import beta_runtime_arguments
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack


class LauncherRuntimeProfileTests(unittest.TestCase):
    def test_profile_overrides_manifest_storage_but_keeps_journal_path(self):
        selection = SimpleNamespace(
            root=Path("/project"), control_relative=Path("control"), instance_id="id",
            manifest_sha256="a" * 64, manifest_path=Path("/project/manifest.toml"),
            project_prefix="EX", project_name="Example", host_root=None, tool_blacklist=[],
            parameters={"runtime": {"workbench": {"storage": "disk"}, "journal": {"storage": "duckdb"}},
                        "paths": {"journal_root": "journal"}},
        )
        with patch.dict(os.environ, {"ANECHOIC_RUNTIME_PROFILE": "dev-local"}, clear=True):
            args = beta_runtime_arguments(selection, "/tmp/socket")
        self.assertNotIn("--workbench-storage", args)
        self.assertNotIn("--journal-storage", args)
        self.assertEqual("journal", args[args.index("--journal-relative") + 1])

    def test_host_defaults_without_changing_selection(self):
        selection = SimpleNamespace(parameters={"runtime": {"workbench": {"storage": "disk"}}})
        args = SimpleNamespace(project_root=Path("/project"), port=1234)
        with (patch.dict(os.environ, {}, clear=True),
              patch.object(host_http, "startup_selection", return_value=selection),
              patch.object(host_http, "native_runtime_gateway", return_value=nullcontext(object())),
              patch.object(host_http, "create_app") as create_app,
              patch.object(host_http.uvicorn, "run")):
            runtime_stack.cache_clear()
            try:
                host_http._serve(args)
                assert os.environ["ANECHOIC_RUNTIME_STACK"] == "beta"
                assert os.environ["ANECHOIC_RUNTIME_PROFILE"] == "dev-local"
                assert create_app.call_args.kwargs["selection"] is selection
                assert selection.parameters["runtime"]["workbench"]["storage"] == "disk"
            finally:
                runtime_stack.cache_clear()

    def test_host_preserves_explicit_profile_and_storage(self):
        args = SimpleNamespace(project_root=Path("/project"), port=1234)
        settings = {"ANECHOIC_RUNTIME_STACK": "beta", "ANECHOIC_RUNTIME_PROFILE": "test",
                    "ANECHOIC_WORKBENCH_STORAGE": "disk", "ANECHOIC_JOURNAL_STORAGE": "duckdb",
                    "ANECHOIC_ARCHIVES": "load"}
        with (patch.dict(os.environ, settings, clear=True),
              patch.object(host_http, "startup_selection", return_value=object()),
              patch.object(host_http, "native_runtime_gateway", return_value=nullcontext(object())),
              patch.object(host_http, "create_app"), patch.object(host_http.uvicorn, "run")):
            runtime_stack.cache_clear()
            try:
                host_http._serve(args)
                assert all(os.environ[key] == value for key, value in settings.items())
            finally:
                runtime_stack.cache_clear()

    def test_host_preserves_explicit_profile_and_rejects_unsupported_stack(self):
        args = SimpleNamespace(project_root=Path("/project"), port=1234)
        with patch.dict(os.environ, {"ANECHOIC_RUNTIME_STACK": "current", "ANECHOIC_RUNTIME_PROFILE": "test"}, clear=True):
            runtime_stack.cache_clear()
            try:
                with self.assertRaisesRegex(ValueError, "requires ANECHOIC_RUNTIME_STACK=beta"):
                    host_http._serve(args)
                assert os.environ["ANECHOIC_RUNTIME_PROFILE"] == "test"
            finally:
                runtime_stack.cache_clear()

    def test_stdio_defaults_and_explicit_overrides(self):
        args = SimpleNamespace(project_root=Path("/project"), control_root=None,
                               instance_id=None, host_project_root=None)
        for initial, expected in (({}, ("beta", "dev-local")),
                                  ({"ANECHOIC_RUNTIME_STACK": "current", "ANECHOIC_RUNTIME_PROFILE": "prod"},
                                   ("current", "prod"))):
            gateway = SimpleNamespace(serve=AsyncMock())
            with (patch.dict(os.environ, initial, clear=True),
                  patch.object(server, "startup_selection", return_value=object()),
                  patch.object(server, "native_runtime_gateway", return_value=nullcontext(gateway))):
                server._serve_stdio(args)
                assert (os.environ["ANECHOIC_RUNTIME_STACK"], os.environ["ANECHOIC_RUNTIME_PROFILE"]) == expected
