"""Check launcher defaults at the supported host and stdio startup entries."""

from contextlib import redirect_stderr
from io import StringIO
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event
from unittest.mock import NonCallableMock
import unittest
from unittest.mock import Mock, patch

import httpx2

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    DirectGateway, beta_runtime_arguments, runtime_stack, server_main,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import supervise_project
from .FEATURE_MCP__tests__shared import write_manifest

HOST_HTTP = Path(__file__).resolve().parents[1] / "host_http.py"
PROFILE_KEYS = {"ANECHOIC_RUNTIME_STACK", "ANECHOIC_RUNTIME_PROFILE", "ANECHOIC_WORKBENCH_STORAGE",
                "ANECHOIC_JOURNAL_STORAGE", "ANECHOIC_ARCHIVES"}


class LauncherRuntimeProfileTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.manifest = write_manifest(self, self.root / "_anechoic_anechoic",
                                       parameters={"runtime": {"workbench": {"storage": "disk"}}})
        self.environment = {key: value for key, value in os.environ.items() if key not in PROFILE_KEYS}
        runtime_stack.cache_clear()
        self.addCleanup(runtime_stack.cache_clear)

    def test_manifest_console_settings_take_precedence_and_legacy_falls_back(self):
        selection = NonCallableMock(
            spec_set=['root', 'control_relative', 'instance_id', 'manifest_sha256',
                'manifest_path', 'project_prefix', 'project_name', 'host_root',
                'tool_blacklist', 'parameters'],

            root=self.root, control_relative=Path("_anechoic_anechoic"),
            instance_id="id", manifest_sha256="hash", manifest_path=self.manifest,
            project_prefix="AN", project_name="Anechoic", host_root=None,
            tool_blacklist=[], parameters={"runtime": {"workbench": {"storage": "memory"}}},
        )
        with patch.dict(os.environ, self.environment, clear=True):
            args = beta_runtime_arguments(selection, "socket")
            self.assertEqual("memory", args[args.index("--workbench-storage") + 1])
            selection.parameters["runtime"]["iwe_console"] = {"storage": "disk", "import_graph": False}
            args = beta_runtime_arguments(selection, "socket")
            self.assertEqual("disk", args[args.index("--workbench-storage") + 1])
            self.assertNotIn("--watch-code", args)

    def host_http(self):
        argv = [str(HOST_HTTP), "--project-root", str(self.root), "--port", "1234"]
        with patch.object(sys, "argv", argv), self.assertRaises(SystemExit) as exited:
            runpy.run_path(str(HOST_HTTP), run_name="__main__")
        return exited.exception.code

    def test_host_defaults_without_changing_selection(self):
        with patch.dict(os.environ, self.environment, clear=True), patch("uvicorn.run") as run:
            self.assertIsNone(self.host_http())
            self.assertEqual(("beta_next", "dev-local"), (os.environ["ANECHOIC_RUNTIME_STACK"],
                                                    os.environ["ANECHOIC_RUNTIME_PROFILE"]))
        run.assert_called_once()
        selection = run.call_args.args[0].gateway.selection
        self.assertEqual(self.manifest, selection.manifest_path)
        self.assertEqual("disk", selection.parameters["runtime"]["workbench"]["storage"])

    def test_host_preserves_explicit_profile_and_storage(self):
        settings = {"ANECHOIC_RUNTIME_STACK": "beta_next", "ANECHOIC_RUNTIME_PROFILE": "test",
                    "ANECHOIC_WORKBENCH_STORAGE": "disk", "ANECHOIC_JOURNAL_STORAGE": "duckdb",
                    "ANECHOIC_ARCHIVES": "load"}
        with patch.dict(os.environ, self.environment | settings, clear=True), patch("uvicorn.run") as run:
            self.assertIsNone(self.host_http())
            self.assertEqual(settings, {key: os.environ[key] for key in settings})
        run.assert_called_once()
        self.assertEqual(self.manifest, run.call_args.args[0].gateway.selection.manifest_path)

    def test_host_preserves_explicit_profile_and_rejects_unsupported_stack(self):
        for stack in ("beta", "current", "unrecognized"):
            settings = {"ANECHOIC_RUNTIME_STACK": stack, "ANECHOIC_RUNTIME_PROFILE": "test"}
            with (self.subTest(stack=stack), patch.dict(os.environ, self.environment | settings, clear=True),
                  patch("uvicorn.run") as run, redirect_stderr(StringIO()) as stderr):
                runtime_stack.cache_clear()
                self.assertEqual(2, self.host_http())
                self.assertEqual("test", os.environ["ANECHOIC_RUNTIME_PROFILE"])
                run.assert_not_called()
            self.assertIn('"event":"mcp_http_startup_failed"', stderr.getvalue())

    def test_stdio_defaults_and_explicit_overrides(self):
        for initial, expected in (({}, ("beta_next", "dev-local")),
                                  ({"ANECHOIC_RUNTIME_STACK": "current", "ANECHOIC_RUNTIME_PROFILE": "prod"},
                                   ("current", "prod"))):
            with (self.subTest(initial=initial), patch.dict(os.environ, self.environment | initial, clear=True),
                  patch.object(DirectGateway, "serve", autospec=True) as serve):
                runtime_stack.cache_clear()
                self.assertIsNone(server_main(["--project-root", str(self.root)]))
                self.assertEqual(expected, (os.environ["ANECHOIC_RUNTIME_STACK"],
                                            os.environ["ANECHOIC_RUNTIME_PROFILE"]))
                serve.assert_awaited_once()
                self.assertEqual(self.manifest, serve.await_args.args[0].selection.manifest_path)


class DirectSupervisorProbe:
    command = [sys.executable, "-B", "fixture-mcp.py"]

    def __init__(self, manifest, *, repair=None, invalid=False, lifecycle=(), diagnostics=None, bound=None):
        self.manifest = manifest
        self.repair = repair
        self.invalid = invalid
        self.lifecycle = iter(lifecycle)
        self.diagnostics, self.bound = diagnostics, bound
        self.real_popen, self.real_wait, self.real_is_socket = subprocess.Popen, Event.wait, Path.is_socket
        self.api_sockets = set()
        self.launched = {"owner": [], "api": [], "mcp": [], "diagnostics": []}
        self.events = []
        self.refusals = []
        self.ready_gates = []
        self.polls = self.stable = 0
        self.gate = None

    def start_child(self, command, **options):
        if command[4:5] and command[4].endswith("project_admission__pub"):
            return self.real_popen(command, **options)
        env = options["env"]
        if command == self.command:
            role = "diagnostics" if env.get("ANECHOIC_BETA_DIRECT_DIAGNOSTICS") == "1" else "mcp"
        else:
            role = "api" if command[-2:] == ["--role", "api"] else "owner"
        self.launched[role].append((command, env))
        self.events.append(("start", role))
        if role == "owner":
            ready = Path(command[command.index("--socket") + 1]).with_name("peers.ready")
            ready.touch()
        if role == "api":
            self.api_sockets.add(Path(command[command.index("--socket") + 1]))
        if role == "diagnostics":
            self.gate = Path(env["ANECHOIC_BETA_DIRECT_TRANSPORT_GATE"])
            self.diagnostics(self.gate)
        if role == "mcp":
            self.gate = Path(env["ANECHOIC_BETA_DIRECT_TRANSPORT_GATE"])
            self.ready_gates.append(self.gate.exists())
            if self.bound is not None:
                self.bound(self.gate)
            if len(self.launched["mcp"]) == 1 and self.repair is not None:
                if self.invalid:
                    self.manifest.write_text("Invalid Manifest")
                else:
                    self.repair()
        child = Mock(poll=Mock(return_value=None), stdin=None if role in ("mcp", "diagnostics") else Mock())

        def wait(timeout):
            self.events.append(("stop", role, timeout))
            child.poll.return_value = 0
            if role == "owner":
                ready.unlink()
            return 0

        child.wait.side_effect = wait
        return child

    def wait_for_event(self, stopping, timeout=None):
        self.polls += 1
        if self.polls > 12:
            raise AssertionError("Supervisor did not complete its fixture cycle")
        if self.diagnostics is not None and not self.launched["owner"]:
            return self.real_wait(stopping, timeout)
        if self.invalid and self.gate is not None and self.gate.exists():
            if self.gate.read_text() == "project_manifest_invalid":
                self.refusals.append(tuple(self.events))
                if len(self.refusals) == 2:
                    self.repair()
        if len(self.launched["mcp"]) == (2 if self.repair is not None else 1):
            self.stable += 1
            if self.stable == 2:
                stopping.set()
        return stopping.is_set()

    def is_socket(self, path):
        return path in self.api_sockets or self.real_is_socket(path)

    def jobs_health(self, path):
        assert path == "/health"
        self.events.append(("lifecycle",))
        args = self.launched["owner"][-1][0]
        instance = args[args.index("--instance-id") + 1]
        return httpx2.Response(200, json={"result": {"instance_id": instance,
                                                    "lifecycle_active": next(self.lifecycle, False)}})

    def run(self, root, stack):
        environment = dict(os.environ, ANECHOIC_RUNTIME_STACK=stack)
        environment.pop("ANECHOIC_RUNTIME_PROFILE", None)
        runtime_stack.cache_clear()
        try:
            with (patch.dict(os.environ, environment, clear=True),
                  patch.object(Event, "wait", autospec=True, side_effect=self.wait_for_event),
                  patch.object(subprocess, "Popen", side_effect=self.start_child),
                  patch.object(Path, "is_socket", autospec=True, side_effect=self.is_socket),
                  patch.object(httpx2, "Client") as client, redirect_stderr(StringIO()) as stderr):
                client.return_value.__enter__.return_value.get.side_effect = self.jobs_health
                result = supervise_project(self.command, environment, root)
            return result, stderr.getvalue()
        finally:
            runtime_stack.cache_clear()


def runtime_flags(command):
    return {name: command[command.index(name) + 1]
            for name in ("--instance-id", "--manifest-sha256", "--workbench-storage", "--socket")}
