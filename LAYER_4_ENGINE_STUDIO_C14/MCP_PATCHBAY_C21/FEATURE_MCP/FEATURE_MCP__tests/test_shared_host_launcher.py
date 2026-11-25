import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import yaml

ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"

from .shared_host_launcher_fixtures import (  # noqa: E402
    IMAGE,
    FakeClock,
    FakeResponse,
    FakeRunner,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import SharedMcpLauncher, shared_mcp_main  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH  # noqa: E402


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

    def _config(self):
        return SharedMcpLauncher().prepare(self.settings, IMAGE)["config"]

    def test_prepare_is_dry_run_and_has_exact_host_bind_inputs(self):
        runner = unittest.mock.Mock()
        result = SharedMcpLauncher(runner=runner).prepare(self.settings, IMAGE)
        self.assertEqual("dry-run", result["mode"])
        self.assertEqual("shared-mcp", result["service"])
        self.assertEqual("54321", result["environment"]["ANECHOIC_MCP_HTTP_PORT"])
        self.assertEqual("INFO", result["environment"]["ANECHOIC_LOG_LEVEL"])
        self.assertNotIn("ANECHOIC_PROJECT_ROOT", result["environment"])
        self.assertEqual([], runner.call_args_list)

    def test_storage_settings_and_host_overrides_reach_compose(self):
        self.settings.write_text(self.settings.read_text() +
                                 '[project_defaults]\nworkbench_storage="memory"\njournal_storage="files"\n')
        names = ("ANECHOIC_WORKBENCH_STORAGE", "ANECHOIC_JOURNAL_STORAGE")
        environment = {key: value for key, value in os.environ.items() if key not in names}
        with patch.dict(os.environ, environment, clear=True):
            defaults = SharedMcpLauncher().prepare(self.settings, IMAGE)["environment"]
            self.assertEqual(("memory", "files"), tuple(defaults[name] for name in names))
            with patch.dict(os.environ, {names[0]: "disk", names[1]: "duckdb"}):
                overrides = SharedMcpLauncher().prepare(self.settings, IMAGE)["environment"]
            self.assertEqual(("disk", "duckdb"), tuple(overrides[name] for name in names))
        compose = yaml.safe_load((Path(__file__).resolve().parents[1] / "docker/shared-mcp.compose.yaml").read_text())
        container_env = compose["services"]["shared-mcp"]["environment"]
        for name in names:
            self.assertIsNone(container_env[name])

    def test_shared_launch_uses_file_logging_level_and_refuses_invalid_level(self):
        existing = self.settings.read_text()
        self.settings.write_text(existing + '[logging]\nlevel="DEBUG"\n')
        runner = unittest.mock.Mock()
        with patch.dict("os.environ", {"ANECHOIC_LOG_LEVEL": "WARNING"}):
            prepared = SharedMcpLauncher(runner=runner).prepare(self.settings, IMAGE)
        self.assertEqual("DEBUG", prepared["environment"]["ANECHOIC_LOG_LEVEL"])
        self.settings.write_text(existing + '[logging]\nlevel="log-level-value"\n')
        with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
            SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        runner.assert_not_called()

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
            result = shared_mcp_main(["--host-settings", str(self.settings), "--image", IMAGE])
        self.assertEqual(0, result)
        runner.assert_not_called()
        self.assertEqual("dry-run", json.loads(output.getvalue())["mode"])

    def test_cli_dry_run_hides_proxy_credentials_but_runtime_env_keeps_proxy(self):
        from subprocess import CompletedProcess

        secret_proxy = "http://proxy-user:proxy-password@example.test:8080"
        runner = unittest.mock.Mock(return_value=CompletedProcess([], 17, "", "daemon unavailable"))
        with patch.dict("os.environ", {"HTTPS_PROXY": secret_proxy}, clear=False):
            result = SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
            output = io.StringIO()
            with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_mcp_launcher.subprocess.run", wraps=__import__("subprocess").run) as docker, redirect_stdout(output):
                cli_result = shared_mcp_main(["--host-settings", str(self.settings), "--image", IMAGE])
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertEqual(secret_proxy, runner.call_args.kwargs["env"]["HTTPS_PROXY"])
        self.assertEqual(0, cli_result)
        docker.assert_not_called()
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
        config = self._config()
        runner = FakeRunner(config, failure=True)
        result = SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        self.assertEqual("docker_start_failed", result["condition"])
        self.assertFalse(result["ready"])

    def test_verify_mcp_uses_the_admitted_port_and_project(self):
        for single, root in ((False, self.projects), (True, self.projects / "alpha")):
            field = "project_root" if single else "projects_root"
            self.settings.write_text(
                f'schema_version=1\n[shared_mcp]\n{field}="{root}"\nhttp_port=54321\n'
            )
            launcher = SharedMcpLauncher(
                runner=FakeRunner(self._config()),
                opener=lambda *_args, **_kwargs: FakeResponse(b'{"state": "ready"}'),
            )
            streams = MagicMock()
            streams.__aenter__.return_value = (object(), object())
            session = MagicMock()
            admitted = session.__aenter__.return_value
            admitted.initialize = AsyncMock()
            admitted.call_tool = AsyncMock(return_value=MagicMock(is_error=False))
            with (self.subTest(single=single),
                  patch("mcp.client.streamable_http.streamable_http_client", return_value=streams) as transport,
                  patch("mcp.client.session.ClientSession", return_value=session)):
                self.assertTrue(launcher.apply(self.settings, IMAGE)["ready"])
                transport.assert_not_called()
                self.assertTrue(launcher.apply(self.settings, IMAGE, verify_mcp=True)["ready"])
                self.assertEqual(f"http://127.0.0.1:54321{MCP_PATH}", transport.call_args.args[0])
                admitted.initialize.assert_awaited_once()
                if single:
                    admitted.call_tool.assert_awaited_once_with("query_schema", {"project_root": str(root)}, read_timeout_seconds=400)
                else:
                    admitted.call_tool.assert_not_awaited()

    def test_mcp_verification_failure_refuses_ready_result(self):
        launcher = SharedMcpLauncher(
            runner=FakeRunner(self._config()),
            opener=lambda *_args, **_kwargs: FakeResponse(b'{"state": "ready"}'),
        )
        with patch("mcp.client.streamable_http.streamable_http_client", side_effect=ValueError("probe failed")):
            result = launcher.apply(self.settings, IMAGE, verify_mcp=True)
        self.assertFalse(result["ready"])
        self.assertEqual("mcp_verification_failed", result["condition"])

    def test_retry_after_start_failure_uses_same_compose_project(self):
        runner = FakeRunner(self._config(), failure=True)
        launcher = SharedMcpLauncher(
            runner=runner, opener=lambda *_args, **_kwargs: FakeResponse(b'{"state": "ready"}')
        )
        first = launcher.apply(self.settings, IMAGE)
        runner.failure = False
        second = launcher.apply(self.settings, IMAGE)
        self.assertFalse(first["ready"])
        self.assertTrue(second["ready"])
        starts = [command for command, _kwargs in runner.commands if "up" in command]
        self.assertEqual(starts[0], starts[1])

    def test_apply_requires_readback_and_health_before_ready(self):
        config = self._config()
        runner = FakeRunner(config)
        health_urls = []

        def open_health(url, **_kwargs):
            health_urls.append(url)
            return FakeResponse(b'{"state": "ready"}')

        result = SharedMcpLauncher(runner=runner, opener=open_health).apply(
            self.settings, IMAGE, readiness_timeout=1
        )
        self.assertEqual("started", result["outcome"])
        self.assertTrue(result["ready"])
        self.assertGreaterEqual(len(runner.commands), 3)
        self.assertEqual([f"http://127.0.0.1:54321{HEALTH_PATH}"], health_urls)

    def test_readiness_budget_starts_after_successful_docker_start(self):
        config = self._config()
        clock = FakeClock()
        runner = FakeRunner(config)

        def run(command, **kwargs):
            result = runner(command, **kwargs)
            if "up" in command:
                clock.advance(31)
            return result

        result = SharedMcpLauncher(
            runner=run,
            opener=lambda *_args, **_kwargs: FakeResponse(b'{"state": "ready"}'),
            sleeper=lambda _seconds: None,
            clock=clock,
        ).apply(self.settings, IMAGE, readiness_timeout=30)
        self.assertTrue(result["ready"])

    def test_readiness_calls_receive_only_remaining_budget(self):
        config = self._config()
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
            return FakeResponse(b'{"state": "ready"}')

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

    def test_unsafe_and_untyped_host_settings_fail_closed(self):
        original = self.settings.read_text()
        settings_link = self.settings.with_name("link.toml")
        settings_link.symlink_to(self.settings)
        oversized = self.settings.with_name("oversized.toml")
        oversized.write_text("#" * 4097)
        fifo = self.settings.with_name("settings.pipe")
        os.mkfifo(fifo)
        runner = unittest.mock.Mock()
        launcher = SharedMcpLauncher(runner=runner)
        for path in (settings_link, oversized, fifo):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
                launcher.apply(path, IMAGE)
        for value in ("true", '"54321"', "65536", "0"):
            self.settings.write_text(original.replace("54321", value))
            with self.subTest(port=value), self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
                launcher.apply(self.settings, IMAGE)
        self.settings.write_text(original)
        self.settings.chmod(0o662)
        with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
            launcher.apply(self.settings, IMAGE)
        runner.assert_not_called()

    def test_default_settings_and_exact_runtime_identity(self):
        from hashlib import sha256

        self.settings.rename(self.settings.with_name("runtime.toml"))
        self.settings.parent.rename(self.settings.parent.with_name("anechoic"))
        default = self.settings.parent.parent / "anechoic/runtime.toml"
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(default.parent.parent)}):
            prepared = SharedMcpLauncher().prepare(None, IMAGE)
        expected = sha256(f"{default}\0{self.projects}".encode()).hexdigest()
        self.assertEqual(str(default), prepared["settings_path"])
        self.assertEqual(expected, prepared["shared_runtime_id"])
        self.assertEqual(2, prepared["max_loaded_projects"])

    def test_settings_path_replace_after_open_refuses_without_docker(self):
        replacement = self.settings.with_name("replacement.toml")
        replacement.write_bytes(self.settings.read_bytes())
        original_open = os.open

        def replace_after_open(path, *args, **kwargs):
            descriptor = original_open(path, *args, **kwargs)
            if path == self.settings:
                replacement.replace(self.settings)
            return descriptor

        runner = unittest.mock.Mock()
        with patch("os.open", side_effect=replace_after_open):
            with self.assertRaisesRegex(ValueError, "^invalid_host_settings$"):
                SharedMcpLauncher(runner=runner).apply(self.settings, IMAGE)
        runner.assert_not_called()

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
