"""Public startup/output contract for the Project MCP launcher."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1]
DOCKER = APP / "docker"
TOOLS = APP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher import (  # noqa: E402
    Launcher,
)


GOLDENS = Path(__file__).parent / "assets" / "launcher_golden" / "startup_output_cases.json"
IMAGE_ID = "sha256:" + "a" * 64
FINGERPRINT = "b" * 64
INSTANCE_ID = "c" * 64


class Backend:
    """Small stateful fake exposing only the launcher's public backend seam."""

    def __init__(self) -> None:
        self.rows = []
        self.resolve_image_calls = 0
        self.image_project_roots = []
        self.start_calls = 0
        self.health_calls = []
        self.inspect_envs = []
        self.start_ports = []
        self.start_error = None
        self.publish_after_start = True
        self.health_result = True
        self.start_entered = threading.Event()
        self.release_start = None

    def resolve_image(self, source_root, explicit_id, *, project_root):
        self.resolve_image_calls += 1
        self.image_project_roots.append(project_root)
        return IMAGE_ID, FINGERPRINT

    def inspect(self, selection):
        environment = dict(os.environ)
        environment.pop("ANECHOIC_MCP_HTTP_SECRET_TOKEN", None)
        self.inspect_envs.append(environment)
        return list(self.rows)

    def start(self, selection, image_id, fingerprint, timeout, port=None):
        self.start_calls += 1
        self.start_ports.append(port)
        self.start_entered.set()
        if self.release_start is not None:
            self.release_start.wait(timeout=2)
        if self.start_error is not None:
            raise self.start_error
        if self.publish_after_start:
            self.rows = [healthy_row(host_port=str(port))]

    def health(self, url, timeout):
        self.health_calls.append((url, timeout))
        return self.health_result


def healthy_row(*, project=INSTANCE_ID, image=IMAGE_ID, fingerprint=FINGERPRINT,
                host_ip="127.0.0.1", host_port="56317", ports=None):
    return {
        "Id": "container-a",
        "Image": image,
        "Config": {"Labels": {
            "org.anechoic.project": project,
            "org.anechoic.runtime.fingerprint": fingerprint,
            "org.anechoic.service": "mcp-http",
        }},
        "State": {"Status": "running", "Health": {"Status": "healthy"}},
        "NetworkSettings": {"Ports": {
            "8092/tcp": ports if ports is not None else [
                {"HostIp": host_ip, "HostPort": host_port}
            ]
        }},
    }


class LauncherStartupFixture:
    def setUp(self) -> None:
        parent = APP.parents[2] / ".anechoic_tmp" / "launcher-epic-1829" / "startup"
        parent.mkdir(parents=True, exist_ok=True)
        self.project_root = Path(tempfile.mkdtemp(dir=parent))
        self.control_root = self.project_root / ".anechoic_local"
        self.control_root.mkdir()
        self.selection = SimpleNamespace(
            root=self.project_root,
            rootPath=self.project_root,
            control_root=self.control_root,
            control_rootPath=self.control_root,
            control_relative=Path(".anechoic_local"),
            control_relativePath=Path(".anechoic_local"),
            instance_id=INSTANCE_ID,
            parameters={"project_mcp": {"http_port": 56317}},
        )
        self.backend = Backend()
        self.launcher = Launcher(backend=self.backend)

    def launch(self, *, token=None, **kwargs):
        kwargs.setdefault("source_root", APP.parents[2])
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher.resolve_project", return_value=self.selection):
            return self.launcher.launch(self.project_root, token, **kwargs)

    def assert_public_failure(self, result, disposition, condition):
        self.assertEqual(disposition, result["disposition"])
        self.assertEqual(condition, result["condition"])
        self.assertNotIn("url", result)

