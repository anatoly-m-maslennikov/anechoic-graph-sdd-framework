"""Focused checks for bounded Docker stdout/stderr retention."""

from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
import re
import runpy
import sys
import unittest
from unittest.mock import patch

import yaml

APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"
ENTRYPOINT = DOCKER / "entrypoint.py"
EXPECTED_LOGGING = {
    "driver": "local",
    "options": {
        "max-size": "10m",
        "max-file": "3",
        "mode": "non-blocking",
        "max-buffer-size": "1m",
    },
}


def _compose(name: str) -> dict[str, object]:
    return yaml.safe_load((DOCKER / name).read_text(encoding="utf-8"))


def _dockerfile():
    text = (DOCKER / "Dockerfile").read_text(encoding="utf-8")
    return re.sub(r"[ \t]*\\\n[ \t]*", " ", text)


class DockerLoggingTests(unittest.TestCase):
    def run_entrypoint(self, mode, *, expected=0):
        with (patch.object(sys, "argv", [str(ENTRYPOINT), mode]),
              patch.object(sys, "path", sys.path.copy()), self.assertRaises(SystemExit) as exit_):
            runpy.run_path(str(ENTRYPOINT), run_name="__main__")
        self.assertEqual(expected, exit_.exception.code)

    def test_all_runtime_services_pass_logging_level_through_compose(self):
        files = ("compose.yaml", "mcp-http.compose.yaml", "project-mcp.compose.yaml", "shared-mcp.compose.yaml")
        for filename in files:
            with self.subTest(filename=filename):
                for service in _compose(filename)["services"].values():
                    self.assertEqual("${ANECHOIC_LOG_LEVEL-INFO}", service["environment"]["ANECHOIC_LOG_LEVEL"])

    def test_direct_entrypoint_defaults_and_hands_off_the_explicit_level(self):
        for environment, expected in (({}, "INFO"), ({"ANECHOIC_LOG_LEVEL": "ERROR"}, "ERROR")):
            with self.subTest(environment=environment), patch.dict(os.environ, environment, clear=True), \
                    patch.object(os, "execve", return_value=None) as start:
                self.run_entrypoint("mcp")
                self.assertEqual(expected, start.call_args.args[2]["ANECHOIC_LOG_LEVEL"])

    def test_direct_entrypoint_rejects_empty_level_without_executing(self):
        output = io.StringIO()
        with (patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": ""}, clear=True),
              patch.object(os, "execve") as start, redirect_stderr(output)):
            self.run_entrypoint("mcp", expected=1)
        start.assert_not_called()
        self.assertEqual({"error": "invalid_log_level", "severity": "ERROR"}, json.loads(output.getvalue()))

    def test_beta_entrypoint_uses_supervised_project_http(self):
        supervisor = "MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor.supervise_project"
        for stack in ("beta_next",):
            environment = {"ANECHOIC_RUNTIME_STACK": stack}
            with self.subTest(stack=stack), patch.dict(os.environ, environment, clear=True), patch(supervisor, return_value=None) as start:
                self.run_entrypoint("mcp-http")
            command, child_env, project = start.call_args.args
            self.assertEqual(stack, child_env["ANECHOIC_RUNTIME_STACK"])
            self.assertEqual("streamable-http", command[command.index("--transport") + 1])
            self.assertEqual(Path("/project"), project)

    def test_beta_next_stdio_entrypoint_starts_server(self):
        with patch.dict(os.environ, {"ANECHOIC_RUNTIME_STACK": "beta_next"}, clear=True), \
                patch.object(os, "execve", return_value=None) as start:
            self.run_entrypoint("mcp")
        command = start.call_args.args[1]
        self.assertIn("MCP_PATCHBAY_C21.FEATURE_MCP.server", command)
        self.assertNotIn("--transport", command)

    def test_shared_entrypoint_selects_the_api_module_and_keeps_the_peer_owner(self):
        supervisor = "MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor._supervise"
        settings, directory = "/settings.toml", Path("/private/runtime")
        for stack, module, owner_module in (
            ("beta_next", "API_MIXER_beta_C91.shared_runtime", "ORCHESTRATOR_beta_C68.shared_peer_owner"),
        ):
            environment = {"ANECHOIC_RUNTIME_STACK": stack, "ANECHOIC_HOST_SETTINGS": settings}
            with self.subTest(stack=stack), patch.dict(os.environ, environment, clear=True), patch(supervisor, return_value=None) as start:
                self.run_entrypoint("shared-mcp")
            command, child_env, configure = start.call_args.args
            self.assertEqual(stack, child_env["ANECHOIC_RUNTIME_STACK"])
            self.assertIn("MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server", command)
            owner, api, _, _ = configure(directory)
            self.assertEqual(owner.command[4:], [
                owner_module, "--socket", str(directory / "owner.sock"),
                "--host-settings", settings,
            ])
            self.assertEqual(api.command[4:], [
                module, "--socket", str(directory / "api.sock"), "--host-settings", settings,
                "--peer-owner-socket", str(directory / "owner.sock"),
            ])
            self.assertEqual(directory / "api.sock", api.socket)

    def test_base_runtime_services_use_bounded_local_logging(self):
        config = _compose("compose.yaml")

        self.assertTrue(
            all(service["logging"] == EXPECTED_LOGGING for service in config["services"].values())
        )

    def test_standalone_runtime_services_use_bounded_local_logging(self):
        for compose_name in ("mcp-http.compose.yaml", "project-mcp.compose.yaml"):
            config = _compose(compose_name)
            self.assertTrue(
                all(
                    service["logging"] == EXPECTED_LOGGING
                    for service in config["services"].values()
                ),
                compose_name,
            )

    def test_base_runtime_has_no_agent_service_or_credential_volume(self):
        config = _compose("compose.yaml")
        self.assertEqual({"mcp"}, set(config["services"]))
        self.assertEqual({"framework-db"}, set(config["volumes"]))

    def test_entrypoint_uses_built_python_without_retained_uv_supervisor(self):
        line = next(line for line in _dockerfile().splitlines()
                    if line.startswith("ENTRYPOINT "))
        self.assertEqual([
            "/opt/venv/bin/python",
            "-B",
            "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py",
        ], json.loads(line.removeprefix("ENTRYPOINT ")))

    def test_image_carries_framework_version_into_workspace(self):
        dockerfile = _dockerfile()
        self.assertRegex(dockerfile, r"(?m)^COPY version\.toml(?: [^ \n]+)* \./$")
        self.assertIn("COPY LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock ./LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/", dockerfile)
        self.assertIn("--mount=type=cache,id=anechoic-uv,target=/tmp/uv-cache uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked", dockerfile)
        self.assertGreater(dockerfile.index("COPY version.toml "), dockerfile.index(" uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked"))


if __name__ == "__main__":
    unittest.main()
