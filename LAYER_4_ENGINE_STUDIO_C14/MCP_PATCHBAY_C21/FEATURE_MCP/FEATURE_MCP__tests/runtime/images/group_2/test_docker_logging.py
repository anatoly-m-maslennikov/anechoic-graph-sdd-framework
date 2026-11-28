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

APP = Path(__file__).resolve().parents[4]
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
    text = re.sub(r"(?<=\S)\\\n(?=\S)", "", text)
    return re.sub(r"[ \t]*\\\n[ \t]*", " ", text)


class DockerLoggingTests(unittest.TestCase):
    def run_entrypoint(self, mode, *, expected=0):
        with (
            patch.object(sys, "argv", [str(ENTRYPOINT), mode]),
            patch.object(sys, "path", sys.path.copy()),
            self.assertRaises(SystemExit) as exit_,
        ):
            runpy.run_path(str(ENTRYPOINT), run_name="__main__")
        self.assertEqual(expected, exit_.exception.code)

    def test_all_runtime_services_pass_logging_level_through_compose(self):
        files = (
            "compose.yaml",
            "mcp-http.compose.yaml",
            "project-mcp.compose.yaml",
            "shared-mcp.compose.yaml",
        )
        for filename in files:
            with self.subTest(filename=filename):
                for service in _compose(filename)["services"].values():
                    self.assertEqual(
                        "${ANECHOIC_LOG_LEVEL-INFO}",
                        service["environment"]["ANECHOIC_LOG_LEVEL"],
                    )

    def test_direct_entrypoint_defaults_and_hands_off_the_explicit_level(self):
        for environment, expected in (
            ({}, "INFO"),
            ({"ANECHOIC_LOG_LEVEL": "ERROR"}, "ERROR"),
        ):
            with (
                self.subTest(environment=environment),
                patch.dict(os.environ, environment, clear=True),
                patch.object(os, "execve", return_value=None) as start,
            ):
                self.run_entrypoint("mcp")
                self.assertEqual(
                    expected, start.call_args.args[2]["ANECHOIC_LOG_LEVEL"]
                )

    def test_direct_entrypoint_rejects_empty_level_without_executing(self):
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": ""}, clear=True),
            patch.object(os, "execve") as start,
            redirect_stderr(output),
        ):
            self.run_entrypoint("mcp", expected=1)
        start.assert_not_called()
        self.assertEqual(
            {"error": "invalid_log_level", "severity": "ERROR"},
            json.loads(output.getvalue()),
        )

    def test_current_entrypoint_starts_the_requested_service(self):
        environment = {
            "ANECHOIC_RUNTIME_STACK": "current",
            "ANECHOIC_HOST_SETTINGS": "/settings.toml",
        }
        for mode, module, flags in (
            ("mcp", "server", ["--project-root", "/project"]),
            (
                "mcp-http",
                "server",
                [
                    "--project-root",
                    "/project",
                    "--transport",
                    "streamable-http",
                ],
            ),
            (
                "shared-mcp",
                "shared_http_server",
                ["--host-settings", "/settings.toml"],
            ),
        ):
            with (
                self.subTest(mode=mode),
                patch.dict(os.environ, environment, clear=True),
                patch.object(os, "execve", return_value=None) as start,
            ):
                self.run_entrypoint(mode)
                _, command, child_env = start.call_args.args
                self.assertEqual(
                    "current", child_env["ANECHOIC_RUNTIME_STACK"]
                )
                self.assertEqual(
                    [f"MCP_PATCHBAY_C21.FEATURE_MCP.{module}", *flags],
                    command[4:],
                )

    def test_entrypoint_refuses_other_runtime_stacks(self):
        for stack in ("beta", "beta_next", "unsupported", ""):
            output = io.StringIO()
            with (
                self.subTest(stack=stack),
                patch.dict(
                    os.environ, {"ANECHOIC_RUNTIME_STACK": stack}, clear=True
                ),
                patch.object(os, "execve") as start,
                redirect_stderr(output),
            ):
                self.run_entrypoint("mcp", expected=1)
                start.assert_not_called()
                self.assertEqual(
                    {"error": "invalid_runtime_stack", "severity": "ERROR"},
                    json.loads(output.getvalue()),
                )

    def test_base_runtime_services_use_bounded_local_logging(self):
        config = _compose("compose.yaml")

        self.assertTrue(
            all(
                service["logging"] == EXPECTED_LOGGING
                for service in config["services"].values()
            )
        )

    def test_standalone_runtime_services_use_bounded_local_logging(self):
        for compose_name in (
            "mcp-http.compose.yaml",
            "project-mcp.compose.yaml",
        ):
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
        line = next(
            line
            for line in _dockerfile().splitlines()
            if line.startswith("ENTRYPOINT ")
        )
        self.assertEqual(
            [
                "/opt/venv/bin/python",
                "-B",
                (
                    "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/"
                    "FEATURE_MCP/docker"
                    "/entrypoint.py"
                ),
            ],
            json.loads(line.removeprefix("ENTRYPOINT ")),
        )

    def test_image_carries_framework_version_into_workspace(self):
        dockerfile = _dockerfile()
        self.assertRegex(
            dockerfile, r"(?m)^COPY version\.toml(?: [^ \n]+)* \./$"
        )
        self.assertIn(
            (
                "COPY LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pypro"
                "ject.toml LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/"
                "uv.lock ./LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/"
            ),
            dockerfile,
        )
        self.assertIn(
            (
                "--mount=type=cache,id=anechoic-uv,target=/tmp/uv-cache uv "
                "sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/en"
                "gine --locked"
            ),
            dockerfile,
        )
        self.assertGreater(
            dockerfile.index("COPY version.toml "),
            dockerfile.index(
                (
                    " uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENT"
                    "S_C72/engine --locked"
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
