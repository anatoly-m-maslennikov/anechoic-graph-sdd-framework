"""Bounded process output and known credential-store image negatives."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import NonCallableMock
from unittest.mock import MagicMock, patch


import selectors

APP = Path(__file__).resolve().parents[4]
import MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared as images  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.backend__shared import (  # noqa: E402
    ProjectMcpBackend,
)  # noqa: E402


IMAGE_ID = "sha256:" + "a" * 64
PRIVATE_MARKER = "synthetic-private-diagnostic"
PROXY_ROUTING = {
    "HTTP_PROXY": "http://proxy.invalid:3128",
    "HTTPS_PROXY": "http://proxy.invalid:3128",
    "ALL_PROXY": "socks5://proxy.invalid:1080",
    "NO_PROXY": "localhost,127.0.0.1",
    "http_proxy": "http://proxy.invalid:3128",
    "https_proxy": "http://proxy.invalid:3128",
    "all_proxy": "socks5://proxy.invalid:1080",
    "no_proxy": "localhost,127.0.0.1",
}


def _tagging_executor(executor, calls):
    tagged, sources, inspections = set(), {}, {}

    def execute(argv, **kwargs):
        command = tuple(argv)
        if command[:3] == ("docker", "image", "tag"):
            calls.append(command)
            tagged.add(command[-1])
            sources[command[-1]] = command[-2]
            return subprocess.CompletedProcess(argv, 0, "", "")
        if command[:3] == ("docker", "image", "inspect") and command[
            -1
        ].startswith("anechoic-runtime:"):
            if command[-1] not in tagged:
                return subprocess.CompletedProcess(argv, 1, "", "")
            payload = json.loads(inspections[sources[command[-1]]])
            payload[0]["RepoTags"] = [command[-1]]
            return subprocess.CompletedProcess(
                argv, 0, json.dumps(payload), ""
            )
        if command[:3] == ("docker", "image", "ls") and command[-1].startswith(
            "anechoic-runtime:"
        ):
            return subprocess.CompletedProcess(argv, 0, "", "")
        result = executor(argv, **kwargs)
        if (
            command[:3] == ("docker", "image", "inspect")
            and result.returncode == 0
        ):
            inspections[command[-1]] = result.stdout
        return result

    return execute


class ImageOutputSafetyTests(unittest.TestCase):
    def python(self, source):
        return [sys.executable, "-B", "-c", source]

    def test_real_reader_rejects_oversize_stdout_before_collecting_it(self):
        with self.assertRaises(ValueError) as raised:
            images._bounded_run(
                self.python("import sys; sys.stdout.write('x' * 1000000)"),
                cwd=APP,
                timeout=2,
                max_output=32,
            )
        self.assertNotIn(PRIVATE_MARKER, str(raised.exception))

    def test_real_reader_discards_noisy_stderr(self):
        source = (
            "import sys; sys.stderr.write('" + PRIVATE_MARKER + "' * 100000); "
            "sys.stdout.write('safe')"
        )
        result = images._bounded_run(
            self.python(source), cwd=APP, timeout=2, max_output=32
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual("safe", result.stdout)
        self.assertEqual("", result.stderr)

    def test_real_build_reader_discards_both_streams(self):
        source = (
            "import sys; sys.stdout.write('x' * 1000000); "
            "sys.stderr.write('y' * 1000000)"
        )
        result = images._bounded_run(
            self.python(source),
            cwd=APP,
            timeout=2,
            capture_stdout=False,
            max_output=32,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("", result.stderr)

    def test_real_reader_timeout_is_finite_and_keeps_no_diagnostics(self):
        source = (
            "import sys,time; sys.stderr.write('" + PRIVATE_MARKER + "'); "
            "sys.stderr.flush(); time.sleep(5)"
        )
        before = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired) as raised:
            images._bounded_run(
                self.python(source), cwd=APP, timeout=0.05, max_output=32
            )
        self.assertLess(time.monotonic() - before, 2)
        self.assertIsNone(raised.exception.output)
        self.assertIsNone(raised.exception.stderr)

    def test_default_executor_routes_to_bounded_reader(self):
        manager = images.ImageManager(
            APP.parents[2], platform="linux/amd64", project_root=APP.parents[2]
        )
        with patch.object(
            images,
            "_bounded_run",
            return_value=subprocess.CompletedProcess([], 0, "[]", ""),
        ) as reader:
            self.assertEqual("[]", manager._run(("docker", "image", "ls")))
        self.assertTrue(reader.call_args.kwargs["capture_stdout"])
        self.assertEqual(
            4 * 1024 * 1024, reader.call_args.kwargs["max_output"]
        )
        with patch.object(
            images,
            "_bounded_run",
            return_value=subprocess.CompletedProcess([], 0, "", ""),
        ) as reader:
            self.assertEqual(
                "", manager._run(("docker", "build"), code="BUILD_FAILED")
            )
        self.assertFalse(reader.call_args.kwargs["capture_stdout"])

    @staticmethod
    def _client_environment():
        client = {
            "HOME": "/synthetic-home",
            "PATH": "/synthetic-bin",
            "DOCKER_HOST": "unix:///synthetic/docker.sock",
            "DOCKER_CONTEXT": "fixture",
            "DOCKER_CONFIG": "/synthetic-docker-config",
            "XDG_RUNTIME_DIR": "/synthetic-runtime",
            "TMPDIR": "/synthetic-tmp",
        }
        client.update(PROXY_ROUTING)
        caller = dict(
            client,
            ANECHOIC_MCP_HTTP_SECRET_TOKEN=PRIVATE_MARKER,
            AWS_SECRET_ACCESS_KEY=PRIVATE_MARKER,
            GITHUB_TOKEN=PRIVATE_MARKER,
            LANG="en_US.UTF-8",
        )
        return client, caller

    def test_default_image_commands_receive_only_the_docker_client_environment(
        self,
    ):
        client, caller = self._client_environment()
        manager = images.ImageManager(
            APP.parents[2], platform="linux/amd64", project_root=APP.parents[2]
        )
        commands = (
            ("docker", "image", "ls"),
            ("docker", "image", "inspect", IMAGE_ID),
            ("docker", "build"),
        )
        for command in commands:
            with self.subTest(command=command):
                process = MagicMock()
                process.wait.return_value = 0
                process.poll.return_value = 0
                process.stdout = None if command[1] == "build" else MagicMock()
                with (
                    patch.dict(os.environ, caller, clear=True),
                    patch.object(
                        images.subprocess, "Popen", return_value=process
                    ) as start,
                    patch.object(selectors, "DefaultSelector") as selector,
                ):
                    selector.return_value.get_map.return_value = {}
                    self.assertEqual("", manager._run(command))
                child_environment = start.call_args.kwargs["env"]
                self.assertEqual(client, child_environment)
                self.assertNotIn(
                    "ANECHOIC_MCP_HTTP_SECRET_TOKEN", child_environment
                )
                self.assertNotIn(PRIVATE_MARKER, child_environment.values())
                for proxy in PROXY_ROUTING.values():
                    self.assertNotIn(proxy, start.call_args.args[0])

    def test_backend_environments_preserve_present_proxy_routing_without_ambient_credentials(
        self,
    ):
        selection = NonCallableMock(
            spec_set=["root", "control_relative", "instance_id"],
            root=APP.parents[2],
            control_relative=Path(".anechoic_fixture"),
            instance_id="c" * 64,
        )
        caller = dict(
            PROXY_ROUTING,
            PATH="/synthetic-bin",
            ANECHOIC_LOG_LEVEL="WARNING",
            ANECHOIC_MCP_HTTP_SECRET_TOKEN=PRIVATE_MARKER,
            AWS_SECRET_ACCESS_KEY=PRIVATE_MARKER,
            GITHUB_TOKEN=PRIVATE_MARKER,
        )
        with patch.dict(os.environ, caller, clear=True):
            client = ProjectMcpBackend._docker_client_environment()
            service = ProjectMcpBackend._environment(
                selection, IMAGE_ID, "b" * 64, 56317
            )
        self.assertEqual(dict(PROXY_ROUTING, PATH="/synthetic-bin"), client)
        self.assertEqual("WARNING", service["ANECHOIC_LOG_LEVEL"])
        for name, value in PROXY_ROUTING.items():
            self.assertEqual(value, service[name])
        self.assertNotIn("ANECHOIC_MCP_HTTP_SECRET_TOKEN", service)
        self.assertNotIn(PRIVATE_MARKER, client.values())
        self.assertNotIn(PRIVATE_MARKER, service.values())
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", service)
        self.assertNotIn("GITHUB_TOKEN", service)
        with patch.dict(os.environ, {"PATH": "/synthetic-bin"}, clear=True):
            absent = ProjectMcpBackend._docker_client_environment()
        self.assertEqual({"PATH": "/synthetic-bin"}, absent)

    def test_mock_oversize_and_timeout_report_only_safe_conditions(self):
        def noisy(argv, **_kwargs):
            return subprocess.CompletedProcess(
                argv, 0, PRIVATE_MARKER * 300000, PRIVATE_MARKER
            )

        manager = images.ImageManager(
            APP.parents[2],
            executor=noisy,
            platform="linux/amd64",
            project_root=APP.parents[2],
        )
        with self.assertRaises(images.ImageError) as raised:
            manager._run(("docker", "image", "ls"))
        self.assertEqual("IMAGE_REFUSED", raised.exception.code)
        self.assertNotIn(PRIVATE_MARKER, str(raised.exception))

        def timeout(argv, **_kwargs):
            raise subprocess.TimeoutExpired(
                argv, 1, PRIVATE_MARKER, PRIVATE_MARKER
            )

        manager = images.ImageManager(
            APP.parents[2],
            executor=timeout,
            platform="linux/amd64",
            project_root=APP.parents[2],
        )
        with self.assertRaises(images.ImageError) as raised:
            manager._run(("docker", "build"), code="BUILD_FAILED")
        self.assertEqual("BUILD_FAILED", raised.exception.code)
        self.assertNotIn(PRIVATE_MARKER, str(raised.exception))
        self.assertTrue(raised.exception.__suppress_context__)
        self.assertIsNone(raised.exception.__cause__)


from ..group_4._runtime_image_credentials import ImageCredentialCases  # noqa: E402


class ImageCredentialContextTests(ImageCredentialCases, unittest.TestCase):
    pass
