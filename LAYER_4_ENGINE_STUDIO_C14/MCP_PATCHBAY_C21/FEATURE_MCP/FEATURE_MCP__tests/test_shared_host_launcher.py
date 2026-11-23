import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"

from .shared_host_launcher_fixtures import (  # noqa: E402
    IMAGE,
    FakeClock,
    FakeResponse,
    FakeRunner,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher import SharedMcpLauncher, main  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker import shared_mcp_launcher  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH  # noqa: E402


class SharedHostLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name).resolve()
        self.projects = base / "My_Repos"
        self.projects.mkdir()
        (self.projects / "alpha").mkdir()
        self.settings = base / "config" / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        self.settings.parent.mkdir()
        self.settings.write_text(
            f'schema_version = 1\n[shared_mcp]\nprojects_root = "{self.projects}"\n'
            "http_port = 54321\nmax_loaded_projects = 2\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_prepare_is_dry_run_and_has_exact_host_bind_inputs(self):
        runner = unittest.mock.Mock()
        result = SharedMcpLauncher(runner=runner).prepare(self.settings, IMAGE)
        self.assertEqual("dry-run", result["mode"])
        self.assertEqual("shared-mcp", result["service"])
        self.assertEqual("54321", result["environment"]["ANECHOIC_MCP_HTTP_PORT"])
        self.assertNotIn("ANECHOIC_PROJECT_ROOT", result["environment"])
        self.assertEqual([], runner.call_args_list)

    def test_single_project_mount_and_cold_start_budget(self):
        root = self.projects / "alpha"
        self.settings.write_text(
            f'schema_version=1\n[shared_mcp]\nproject_root="{root}"\nhttp_port=54321\n'
        )
        result = SharedMcpLauncher().prepare(self.settings, IMAGE)
        self.assertEqual(str(root), result["environment"]["ANECHOIC_PROJECTS_ROOT"])
        self.assertEqual("420", result["command"][-2])

    def test_cli_dry_run_exits_success_without_docker(self):
        output = io.StringIO()
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher.subprocess.run", wraps=__import__("subprocess").run) as runner, redirect_stdout(output):
            result = main(["--host-settings", str(self.settings), "--image", IMAGE])
        self.assertEqual(0, result)
        self.assertTrue(all(call.args[0][0] == sys.executable for call in runner.call_args_list))
        self.assertEqual("dry-run", json.loads(output.getvalue())["mode"])

    def test_cli_dry_run_hides_proxy_credentials_but_runtime_env_keeps_proxy(self):
        from subprocess import CompletedProcess

        secret_proxy = "http://proxy-user:proxy-password@example.test:8080"
        runner = unittest.mock.Mock(return_value=CompletedProcess([], 17, "", "daemon unavailable"))
        with patch.dict("os.environ", {"HTTPS_PROXY": secret_proxy}, clear=False):
            result = SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
            output = io.StringIO()
            with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher.subprocess.run", wraps=__import__("subprocess").run) as docker, redirect_stdout(output):
                cli_result = main(["--host-settings", str(self.settings), "--image", IMAGE])
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertEqual(secret_proxy, runner.call_args.kwargs["env"]["HTTPS_PROXY"])
        self.assertEqual(0, cli_result)
        self.assertTrue(all(call.args[0][0] == sys.executable for call in docker.call_args_list))
        public = json.loads(output.getvalue())
        self.assertNotIn(secret_proxy, output.getvalue())
        self.assertNotIn("proxy-password", output.getvalue())
        self.assertTrue(all(key.startswith("ANECHOIC_") for key in public["environment"]))

    def test_requires_explicit_immutable_image_without_docker(self):
        runner = unittest.mock.Mock()
        with self.assertRaises(ValueError):
            SharedMcpLauncher(runner=runner).prepare(self.settings, "anechoic-runtime:local")
        runner.assert_not_called()

    def test_compose_is_one_loopback_service_with_two_exact_bind_mounts(self):
        compose = Path(__file__).resolve().parents[1] / "docker/shared-mcp.compose.yaml"
        service = yaml.safe_load(compose.read_text(encoding="utf-8"))["services"]["shared-mcp"]
        self.assertEqual(["shared-mcp"], service["command"])
        self.assertEqual("no", service["restart"])
        self.assertTrue(service["read_only"])
        self.assertEqual(3, len(service["volumes"]))
        self.assertEqual({"bind", "volume"}, {item["type"] for item in service["volumes"]})
        self.assertNotIn("docker.sock", compose.read_text(encoding="utf-8"))
        self.assertEqual(
            ["127.0.0.1:${ANECHOIC_MCP_HTTP_PORT:?Shared HTTP port is required}:8092"],
            service["ports"],
        )

    def test_apply_reports_docker_failure_without_ready_claim(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        config = load_host_runtime_config(self.settings)
        runner = FakeRunner(config, failure=True)
        result = SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertFalse(result["ready"])

    def test_verify_mcp_uses_the_admitted_port_and_project(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        for single, root in ((False, self.projects), (True, self.projects / "alpha")):
            field = "project_root" if single else "projects_root"
            self.settings.write_text(
                f'schema_version=1\n[shared_mcp]\n{field}="{root}"\nhttp_port=54321\n'
            )
            launcher = SharedMcpLauncher(
                runner=FakeRunner(load_host_runtime_config(self.settings)),
                opener=lambda *_args, **_kwargs: FakeResponse(b'{"ready": true}'),
            )
            with self.subTest(single=single), patch.object(shared_mcp_launcher, "_probe") as probe:
                self.assertTrue(launcher.apply(self.settings, IMAGE)["ready"])
                probe.assert_not_awaited()
                self.assertTrue(launcher.apply(self.settings, IMAGE, verify_mcp=True)["ready"])
                probe.assert_awaited_once_with(54321, root if single else None)

    def test_mcp_verification_failure_refuses_ready_result(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        launcher = SharedMcpLauncher(
            runner=FakeRunner(load_host_runtime_config(self.settings)),
            opener=lambda *_args, **_kwargs: FakeResponse(b'{"ready": true}'),
        )
        with patch.object(shared_mcp_launcher, "_probe", side_effect=ValueError("probe failed")):
            result = launcher.apply(self.settings, IMAGE, verify_mcp=True)
        self.assertFalse(result["ready"])
        self.assertEqual("mcp_verification_failed", result["condition"])

    def test_retry_after_start_failure_uses_same_compose_project(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        runner = FakeRunner(load_host_runtime_config(self.settings), failure=True)
        launcher = SharedMcpLauncher(
            runner=runner, opener=lambda *_args, **_kwargs: FakeResponse(b'{"ready": true}')
        )
        first = launcher.apply(self.settings, IMAGE)
        runner.failure = False
        second = launcher.apply(self.settings, IMAGE)
        self.assertFalse(first["ready"])
        self.assertTrue(second["ready"])
        starts = [command for command, _kwargs in runner.commands if "up" in command]
        self.assertEqual(starts[0], starts[1])

    def test_apply_requires_readback_and_health_before_ready(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        config = load_host_runtime_config(self.settings)
        runner = FakeRunner(config)
        health_urls = []

        def open_health(url, **_kwargs):
            health_urls.append(url)
            return FakeResponse(b'{"ready": true}')

        result = SharedMcpLauncher(runner=runner, opener=open_health).apply(
            self.settings, IMAGE, readiness_timeout=1
        )
        self.assertEqual("started", result["outcome"])
        self.assertTrue(result["ready"])
        self.assertGreaterEqual(len(runner.commands), 3)
        self.assertEqual([f"http://127.0.0.1:54321{HEALTH_PATH}"], health_urls)

    def test_readiness_budget_starts_after_successful_docker_start(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        config = load_host_runtime_config(self.settings)
        clock = FakeClock()
        runner = FakeRunner(config)

        def run(command, **kwargs):
            result = runner(command, **kwargs)
            if "up" in command:
                clock.advance(31)
            return result

        result = SharedMcpLauncher(
            runner=run,
            opener=lambda *_args, **_kwargs: FakeResponse(b'{"ready": true}'),
            sleeper=lambda _seconds: None,
            clock=clock,
        ).apply(self.settings, IMAGE, readiness_timeout=30)
        self.assertTrue(result["ready"])

    def test_readiness_calls_receive_only_remaining_budget(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config

        config = load_host_runtime_config(self.settings)
        clock = FakeClock()
        runner = FakeRunner(config)
        docker_timeouts = []

        def run(command, **kwargs):
            result = runner(command, **kwargs)
            if "up" not in command:
                docker_timeouts.append(kwargs["timeout"])
                if command[-4:] == ["ps", "--all", "-q", "shared-mcp"]:
                    clock.advance(0.99)
            return result

        health_timeouts = []

        def open_health(_url, *, timeout):
            health_timeouts.append(timeout)
            return FakeResponse(b'{"ready": true}')

        result = SharedMcpLauncher(
            runner=run,
            opener=open_health,
            sleeper=lambda _seconds: None,
            clock=clock,
        ).apply(self.settings, IMAGE, readiness_timeout=1)
        self.assertTrue(result["ready"])
        self.assertTrue(docker_timeouts)
        self.assertLessEqual(max(docker_timeouts), 1)
        self.assertEqual(1, len(health_timeouts))
        self.assertLessEqual(health_timeouts[0], 0.02)

    def test_backend_response_errors_fail_closed(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launch_support import _config

        responses = [
            subprocess.CompletedProcess([], 0, "{}", ""),
            subprocess.TimeoutExpired("settings", 10),
        ]
        for response in responses:
            with self.subTest(response=response):
                kwargs = {"side_effect": response} if isinstance(response, Exception) else {"return_value": response}
                with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launch_support.subprocess.run", **kwargs):
                    with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
                        _config(self.settings)

    def test_invalid_host_settings_refuse_without_docker(self):
        runner = unittest.mock.Mock()
        with patch.dict(
            "os.environ", {"XDG_CONFIG_HOME": str(Path(self.temp.name) / "missing")}, clear=False
        ):
            with self.assertRaises(ValueError):
                SharedMcpLauncher(runner=runner).prepare(None, IMAGE)
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
