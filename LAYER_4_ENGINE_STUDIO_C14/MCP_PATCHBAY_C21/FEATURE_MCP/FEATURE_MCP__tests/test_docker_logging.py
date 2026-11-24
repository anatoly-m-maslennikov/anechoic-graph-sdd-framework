"""Focused checks for bounded Docker stdout/stderr retention."""

import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

from MCP_PATCHBAY_C21.FEATURE_MCP.docker import entrypoint


APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"
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


class DockerLoggingTests(unittest.TestCase):
    def test_all_runtime_services_pass_logging_level_through_compose(self):
        files = ("compose.yaml", "mcp-http.compose.yaml", "project-mcp.compose.yaml", "shared-mcp.compose.yaml")
        for filename in files:
            with self.subTest(filename=filename):
                for service in _compose(filename)["services"].values():
                    self.assertEqual("${ANECHOIC_LOG_LEVEL-INFO}", service["environment"]["ANECHOIC_LOG_LEVEL"])

    def test_direct_entrypoint_defaults_and_hands_off_the_explicit_level(self):
        for environment, expected in (({}, "INFO"), ({"ANECHOIC_LOG_LEVEL": "ERROR"}, "ERROR")):
            with self.subTest(environment=environment), patch.dict(os.environ, environment, clear=True), \
                    patch.object(os, "execve") as start:
                entrypoint._exec_service("mcp")
                self.assertEqual(expected, start.call_args.args[2]["ANECHOIC_LOG_LEVEL"])

    def test_direct_entrypoint_rejects_empty_level_without_executing(self):
        with patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": ""}, clear=True), patch.object(os, "execve") as start:
            with self.assertRaisesRegex(entrypoint.ExplicitStartupFailure, "invalid_log_level"):
                entrypoint._exec_service("mcp")
        start.assert_not_called()

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
        line = next(line for line in (DOCKER / "Dockerfile").read_text().splitlines()
                    if line.startswith("ENTRYPOINT "))
        self.assertEqual([
            "/opt/venv/bin/python",
            "-B",
            "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py",
        ], json.loads(line.removeprefix("ENTRYPOINT ")))

    def test_image_carries_framework_version_into_workspace(self):
        dockerfile = (DOCKER / "Dockerfile").read_text(encoding="utf-8")
        self.assertRegex(dockerfile, r"(?m)^COPY version\.toml(?: [^ \n]+)* \./$")
        self.assertIn("COPY LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock ./LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/", dockerfile)
        self.assertIn("--mount=type=cache,id=anechoic-uv,target=/tmp/uv-cache uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked", dockerfile)
        self.assertGreater(dockerfile.index("COPY version.toml "), dockerfile.index(" uv sync --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine --locked"))


if __name__ == "__main__":
    unittest.main()
