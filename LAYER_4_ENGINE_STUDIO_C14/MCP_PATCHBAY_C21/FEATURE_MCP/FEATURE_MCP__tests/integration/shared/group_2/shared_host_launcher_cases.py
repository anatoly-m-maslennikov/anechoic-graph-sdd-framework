import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[7]
TOOLS = ROOT / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"

from ..group_3.shared_host_launcher_fixtures import IMAGE  # noqa: E402
from ..group_3.shared_host_launcher_fixtures import FakeResponse  # noqa: E402
from ..group_3.shared_host_launcher_fixtures import FakeRunner  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    SharedMcpLauncher,
    shared_mcp_main,
)  # noqa: E402


class _SharedHostLauncherCases:
    def test_prepare_is_dry_run_and_has_exact_host_bind_inputs(self):
        runner = unittest.mock.Mock()
        result = SharedMcpLauncher(runner=runner).prepare(self.settings, IMAGE)
        self.assertEqual("dry-run", result["mode"])
        self.assertEqual("shared-mcp", result["service"])
        self.assertEqual(
            "54321", result["environment"]["ANECHOIC_MCP_HTTP_PORT"]
        )
        self.assertEqual("INFO", result["environment"]["ANECHOIC_LOG_LEVEL"])
        self.assertNotIn("ANECHOIC_PROJECT_ROOT", result["environment"])
        self.assertEqual([], runner.call_args_list)

    def test_storage_settings_and_host_overrides_reach_compose(self):
        self.settings.write_text(
            self.settings.read_text()
            + (
                '[project_defaults]\nworkbench_storage="memory"\n'
                'journal_storage="files"\n'
            )
        )
        names = ("ANECHOIC_WORKBENCH_STORAGE", "ANECHOIC_JOURNAL_STORAGE")
        environment = {
            key: value for key, value in os.environ.items() if key not in names
        }
        with patch.dict(os.environ, environment, clear=True):
            defaults = SharedMcpLauncher().prepare(self.settings, IMAGE)[
                "environment"
            ]
            self.assertEqual(
                ("memory", "files"), tuple(defaults[name] for name in names)
            )
            with patch.dict(
                os.environ, {names[0]: "disk", names[1]: "duckdb"}
            ):
                overrides = SharedMcpLauncher().prepare(self.settings, IMAGE)[
                    "environment"
                ]
            self.assertEqual(
                ("disk", "duckdb"), tuple(overrides[name] for name in names)
            )
        compose = yaml.safe_load(
            (
                Path(__file__).resolve().parents[4]
                / "docker/shared-mcp.compose.yaml"
            ).read_text()
        )
        container_env = compose["services"]["shared-mcp"]["environment"]
        for name in names:
            self.assertIsNone(container_env[name])

    def test_shared_launch_uses_file_logging_level_and_refuses_invalid_level(
        self,
    ):
        existing = self.settings.read_text()
        self.settings.write_text(existing + '[logging]\nlevel="DEBUG"\n')
        runner = unittest.mock.Mock()
        with patch.dict("os.environ", {"ANECHOIC_LOG_LEVEL": "WARNING"}):
            prepared = SharedMcpLauncher(runner=runner).prepare(
                self.settings, IMAGE
            )
        self.assertEqual(
            "DEBUG", prepared["environment"]["ANECHOIC_LOG_LEVEL"]
        )
        self.settings.write_text(
            existing + '[logging]\nlevel="log-level-value"\n'
        )
        with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
            SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        runner.assert_not_called()

    def test_single_project_mount_and_cold_start_budget(self):
        root = self.projects / "alpha"
        self.settings.write_text(
            (
                'schema_version=1\n[shared_mcp]\nproject_root="'
                f"{root}"
                '"\nhttp_port=54321\n'
            )
        )
        result = SharedMcpLauncher().prepare(self.settings, IMAGE)
        self.assertEqual(
            str(root), result["environment"]["ANECHOIC_PROJECTS_ROOT"]
        )
        self.assertEqual("420", result["command"][-2])

    def test_cli_dry_run_exits_success_without_docker(self):
        output = io.StringIO()
        with (
            patch(
                (
                    "MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher."
                    "subprocess.run"
                ),
                wraps=__import__("subprocess").run,
            ) as runner,
            redirect_stdout(output),
        ):
            result = shared_mcp_main([
                "--host-settings",
                str(self.settings),
                "--image",
                IMAGE,
            ])
        self.assertEqual(0, result)
        runner.assert_not_called()
        self.assertEqual("dry-run", json.loads(output.getvalue())["mode"])

    def test_cli_dry_run_hides_proxy_credentials_but_runtime_env_keeps_proxy(
        self,
    ):
        from subprocess import CompletedProcess

        secret_proxy = "http://proxy-user:proxy-password@example.test:8080"
        runner = unittest.mock.Mock(
            return_value=CompletedProcess([], 17, "", "daemon unavailable")
        )
        with patch.dict(
            "os.environ", {"HTTPS_PROXY": secret_proxy}, clear=False
        ):
            result = SharedMcpLauncher(runner=runner).apply(
                self.settings, IMAGE
            )
            output = io.StringIO()
            with (
                patch(
                    (
                        "MCP_PATCHBAY_C21.FEATURE_MCP.docker."
                        "shared_mcp_launcher.subprocess.run"
                    ),
                    wraps=__import__("subprocess").run,
                ) as docker,
                redirect_stdout(output),
            ):
                cli_result = shared_mcp_main([
                    "--host-settings",
                    str(self.settings),
                    "--image",
                    IMAGE,
                ])
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertEqual(
            secret_proxy, runner.call_args.kwargs["env"]["HTTPS_PROXY"]
        )
        self.assertEqual(0, cli_result)
        docker.assert_not_called()
        public = json.loads(output.getvalue())
        self.assertNotIn(secret_proxy, output.getvalue())
        self.assertNotIn("proxy-password", output.getvalue())
        self.assertTrue(
            all(key.startswith("ANECHOIC_") for key in public["environment"])
        )

    def test_requires_explicit_immutable_image_without_docker(self):
        runner = unittest.mock.Mock()
        with self.assertRaises(ValueError):
            SharedMcpLauncher(runner=runner).prepare(
                self.settings, "anechoic-runtime:local"
            )
        runner.assert_not_called()

    def test_compose_is_one_loopback_service_with_two_exact_bind_mounts(self):
        compose = (
            Path(__file__).resolve().parents[4]
            / "docker/shared-mcp.compose.yaml"
        )
        service = yaml.safe_load(compose.read_text(encoding="utf-8"))[
            "services"
        ]["shared-mcp"]
        self.assertEqual(["shared-mcp"], service["command"])
        self.assertEqual("no", service["restart"])
        self.assertTrue(service["read_only"])
        self.assertEqual(3, len(service["volumes"]))
        self.assertEqual(
            {"bind", "volume"}, {item["type"] for item in service["volumes"]}
        )
        self.assertNotIn("docker.sock", compose.read_text(encoding="utf-8"))
        self.assertEqual(
            [
                (
                    "127.0.0.1:${ANECHOIC_MCP_HTTP_PORT:?Shared HTTP port is "
                    "required}:8092"
                )
            ],
            service["ports"],
        )

    def test_apply_reports_docker_failure_without_ready_claim(self):
        config = self._config()
        runner = FakeRunner(config, failure=True)
        result = SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertFalse(result["ready"])

    def test_verify_mcp_uses_the_admitted_port_and_project(self):
        for single, root in (
            (False, self.projects),
            (True, self.projects / "alpha"),
        ):
            with (
                self.subTest(single=single),
            ):
                self._assert_mcp_verification(single, root)

    def test_mcp_verification_failure_refuses_ready_result(self):
        launcher = SharedMcpLauncher(
            runner=FakeRunner(self._config()),
            opener=lambda *_args, **_kwargs: FakeResponse(
                b'{"state": "ready"}'
            ),
        )
        with patch(
            "mcp.client.streamable_http.streamable_http_client",
            side_effect=ValueError("probe failed"),
        ):
            result = launcher.apply(self.settings, IMAGE, verify_mcp=True)
        self.assertFalse(result["ready"])
        self.assertEqual("mcp_verification_failed", result["condition"])
