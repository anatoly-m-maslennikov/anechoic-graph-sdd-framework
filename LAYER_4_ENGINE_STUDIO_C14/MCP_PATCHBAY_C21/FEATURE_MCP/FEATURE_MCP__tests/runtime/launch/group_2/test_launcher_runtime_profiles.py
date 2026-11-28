"""Check launcher defaults at the supported host and stdio startup entries."""

from contextlib import redirect_stderr
from io import StringIO
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    DirectGateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    runtime_stack,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    server_main,
)
from ....FEATURE_MCP__tests__shared import write_manifest

HOST_HTTP = Path(__file__).resolve().parents[4] / "host_http.py"
PROFILE_KEYS = {
    "ANECHOIC_RUNTIME_STACK",
    "ANECHOIC_RUNTIME_PROFILE",
    "ANECHOIC_WORKBENCH_STORAGE",
    "ANECHOIC_JOURNAL_STORAGE",
    "ANECHOIC_ARCHIVES",
}


class LauncherRuntimeProfileTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.manifest = write_manifest(
            self,
            self.root / "_anechoic_anechoic",
            parameters={"runtime": {"workbench": {"storage": "disk"}}},
        )
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key not in PROFILE_KEYS
        }
        runtime_stack.cache_clear()
        self.addCleanup(runtime_stack.cache_clear)

    def host_http(self):
        argv = [
            str(HOST_HTTP),
            "--project-root",
            str(self.root),
            "--port",
            "1234",
        ]
        with (
            patch.object(sys, "argv", argv),
            self.assertRaises(SystemExit) as exited,
        ):
            runpy.run_path(str(HOST_HTTP), run_name="__main__")
        return exited.exception.code

    def test_host_defaults_without_changing_selection(self):
        with (
            patch.dict(os.environ, self.environment, clear=True),
            patch("uvicorn.run") as run,
        ):
            self.assertIsNone(self.host_http())
            self.assertEqual(
                (None, "dev-local"),
                (
                    os.environ.get("ANECHOIC_RUNTIME_STACK"),
                    os.environ["ANECHOIC_RUNTIME_PROFILE"],
                ),
            )
        run.assert_called_once()
        selection = run.call_args.args[0].gateway.selection
        self.assertEqual(self.manifest, selection.manifest_path)
        self.assertEqual(
            "disk", selection.parameters["runtime"]["workbench"]["storage"]
        )

    def test_host_preserves_explicit_profile_and_storage(self):
        settings = {
            "ANECHOIC_RUNTIME_STACK": "current",
            "ANECHOIC_RUNTIME_PROFILE": "test",
            "ANECHOIC_WORKBENCH_STORAGE": "disk",
            "ANECHOIC_JOURNAL_STORAGE": "duckdb",
            "ANECHOIC_ARCHIVES": "load",
        }
        with (
            patch.dict(os.environ, self.environment | settings, clear=True),
            patch("uvicorn.run") as run,
        ):
            self.assertIsNone(self.host_http())
            self.assertEqual(
                settings, {key: os.environ[key] for key in settings}
            )
        run.assert_called_once()
        self.assertEqual(
            self.manifest,
            run.call_args.args[0].gateway.selection.manifest_path,
        )

    def test_host_preserves_explicit_profile_and_rejects_unsupported_stack(
        self,
    ):
        for stack in ("beta", "beta_next", "unrecognized", ""):
            settings = {
                "ANECHOIC_RUNTIME_STACK": stack,
                "ANECHOIC_RUNTIME_PROFILE": "test",
            }
            with (
                self.subTest(stack=stack),
                patch.dict(
                    os.environ, self.environment | settings, clear=True
                ),
                patch("uvicorn.run") as run,
                redirect_stderr(StringIO()) as stderr,
            ):
                runtime_stack.cache_clear()
                self.assertEqual(2, self.host_http())
                self.assertEqual(
                    "test", os.environ["ANECHOIC_RUNTIME_PROFILE"]
                )
                run.assert_not_called()
            self.assertIn(
                '"event":"mcp_http_startup_failed"', stderr.getvalue()
            )

    def test_stdio_defaults_and_explicit_overrides(self):
        for initial, expected in (
            ({}, (None, "dev-local")),
            (
                {
                    "ANECHOIC_RUNTIME_STACK": "current",
                    "ANECHOIC_RUNTIME_PROFILE": "prod",
                },
                ("current", "prod"),
            ),
        ):
            with (
                self.subTest(initial=initial),
                patch.dict(os.environ, self.environment | initial, clear=True),
                patch.object(DirectGateway, "serve", autospec=True) as serve,
            ):
                runtime_stack.cache_clear()
                self.assertIsNone(
                    server_main(["--project-root", str(self.root)])
                )
                self.assertEqual(
                    expected,
                    (
                        os.environ.get("ANECHOIC_RUNTIME_STACK"),
                        os.environ["ANECHOIC_RUNTIME_PROFILE"],
                    ),
                )
                serve.assert_awaited_once()
                self.assertEqual(
                    self.manifest,
                    serve.await_args.args[0].selection.manifest_path,
                )
