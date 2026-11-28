import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from .shared_host_launcher_cases import _SharedHostLauncherCases

ROOT = Path(__file__).resolve().parents[7]
TOOLS = ROOT / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"

from ..group_3.shared_host_launcher_fixtures import IMAGE  # noqa: E402
from ..group_3.shared_host_launcher_fixtures import FakeClock  # noqa: E402
from ..group_3.shared_host_launcher_fixtures import FakeResponse  # noqa: E402
from ..group_3.shared_host_launcher_fixtures import FakeRunner  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    SharedMcpLauncher,
)  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.paths__shared import (  # noqa: E402
    HEALTH_PATH,
    MCP_PATH,
)  # noqa: E402


class SharedHostLauncherTests(_SharedHostLauncherCases, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name).resolve()
        self.projects = base / "My_Repos"
        self.projects.mkdir()
        (self.projects / "alpha").mkdir()
        self.settings = (
            base
            / "config"
            / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        )
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

    def _assert_mcp_verification(self, single, root):
        field = "project_root" if single else "projects_root"
        self.settings.write_text(
            f'schema_version=1\n[shared_mcp]\n{field}="{root}"\nhttp_port=54321\n'
        )
        launcher = SharedMcpLauncher(
            runner=FakeRunner(self._config()),
            opener=lambda *_args, **_kwargs: FakeResponse(
                b'{"state": "ready"}'
            ),
        )
        streams = MagicMock()
        streams.__aenter__.return_value = (object(), object())
        session = MagicMock()
        admitted = session.__aenter__.return_value
        admitted.initialize = AsyncMock()
        admitted.call_tool = AsyncMock(return_value=MagicMock(is_error=False))
        with (
            patch(
                "mcp.client.streamable_http.streamable_http_client",
                return_value=streams,
            ) as transport,
            patch("mcp.client.session.ClientSession", return_value=session),
        ):
            self.assertTrue(launcher.apply(self.settings, IMAGE)["ready"])
            transport.assert_not_called()
            self.assertTrue(
                launcher.apply(self.settings, IMAGE, verify_mcp=True)["ready"]
            )
        self.assertEqual(
            f"http://127.0.0.1:54321{MCP_PATH}", transport.call_args.args[0]
        )
        admitted.initialize.assert_awaited_once()
        if single:
            admitted.call_tool.assert_awaited_once_with(
                "query_schema",
                {"project_root": str(root)},
                read_timeout_seconds=400,
            )
        else:
            admitted.call_tool.assert_not_awaited()

    def test_retry_after_start_failure_uses_same_compose_project(self):
        runner = FakeRunner(self._config(), failure=True)
        launcher = SharedMcpLauncher(
            runner=runner,
            opener=lambda *_args, **_kwargs: FakeResponse(
                b'{"state": "ready"}'
            ),
        )
        first = launcher.apply(self.settings, IMAGE)
        runner.failure = False
        second = launcher.apply(self.settings, IMAGE)
        self.assertFalse(first["ready"])
        self.assertTrue(second["ready"])
        starts = [
            command for command, _kwargs in runner.commands if "up" in command
        ]
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
            opener=lambda *_args, **_kwargs: FakeResponse(
                b'{"state": "ready"}'
            ),
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
            with (
                self.subTest(path=path),
                self.assertRaisesRegex(ValueError, "^invalid_host_settings$"),
            ):
                launcher.apply(path, IMAGE)
        for value in ("true", '"54321"', "65536", "0"):
            self.settings.write_text(original.replace("54321", value))
            with (
                self.subTest(port=value),
                self.assertRaisesRegex(ValueError, "^invalid_host_settings$"),
            ):
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
        with patch.dict(
            os.environ, {"XDG_CONFIG_HOME": str(default.parent.parent)}
        ):
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
            "os.environ",
            {"XDG_CONFIG_HOME": str(Path(self.temp.name) / "missing")},
            clear=False,
        ):
            with self.assertRaises(ValueError):
                SharedMcpLauncher(runner=runner).prepare(None, IMAGE)
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
