"""Production container startup and ownership checks."""

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import NonCallableMock

from LAYER_1_RUNTIME_IMAGES_C81.release_container import start_container


class ContainerFixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.selection = NonCallableMock(
            spec_set=["root", "control_relative", "instance_id"],
            root=self.root,
            control_relative=Path(".anechoic"),
            instance_id="a" * 64,
        )
        self.image = "sha256:" + "b" * 64
        self.fingerprint = "c" * 64
        self.identifier = "d" * 64
        self.calls = []
        self.logs = ""
        self.row = self._container_row()

    def _container_row(self):
        return {
            "Id": self.identifier,
            "Image": self.image,
            "State": {"Running": True, "Health": {"Status": "healthy"}},
            "Config": {
                "Labels": {
                    "org.anechoic.project": self.selection.instance_id,
                    "org.anechoic.runtime.fingerprint": self.fingerprint,
                    "org.anechoic.service": "mcp-http",
                    "org.anechoic.control_root": ".anechoic",
                    "org.anechoic.host_project_root": str(self.root),
                }
            },
            "NetworkSettings": {
                "Ports": {
                    "8092/tcp": [{"HostIp": "127.0.0.1", "HostPort": "18092"}]
                }
            },
            "Mounts": [
                {
                    "Type": "volume",
                    "Name": "anechoic-framework-db",
                    "Destination": "/var/lib/anechoic",
                    "RW": True,
                },
                {
                    "Type": "bind",
                    "Source": str(self.root),
                    "Destination": "/project",
                    "RW": True,
                },
            ],
        }

    def run_docker(self, argv, root):
        self.calls.append(argv)
        self.assertEqual(root, self.root)
        if argv[1] == "logs":
            return subprocess.CompletedProcess(argv, 0, "", self.logs)
        output = self.identifier if argv[1] == "run" else ""
        if argv[2] == "inspect":
            output = json.dumps(
                self.row if argv[-2] == "{{json .}}" else self.diagnostic_row()
            )
        return subprocess.CompletedProcess(argv, 0, output, "")

    def diagnostic_row(self):
        state = self.row["State"]
        return {
            "id": self.row["Id"],
            "labels": self.row["Config"]["Labels"],
            "status": state.get("Status"),
            "running": state["Running"],
            "health": state["Health"]["Status"],
            "oom_killed": state.get("OOMKilled"),
            "exit_code": state.get("ExitCode"),
            "memory_limit_bytes": 1610612736,
            "nano_cpus": 1000000000,
        }

    def stop_candidate(self):
        self.row["State"].update(
            Running=False, Status="exited", OOMKilled=True, ExitCode=137
        )
        self.row["HostConfig"] = {
            "PortBindings": self.row["NetworkSettings"]["Ports"]
        }

    def start(self, evidence=None):
        return start_container(
            self.root,
            self.selection,
            self.image,
            self.fingerprint,
            18092,
            self.run_docker,
            evidence=evidence,
        )

    def _failed_bind_docker(self, label, label_value):
        def docker(argv, root):
            if argv[1] == "run":
                self.calls.append(argv)
                return subprocess.CompletedProcess(
                    argv, 125, "", "bind: address already in use"
                )
            if argv[:3] == ("docker", "container", "ls"):
                self.calls.append(argv)
                self.assertIn(f"label={label}={label_value}", argv)
                return subprocess.CompletedProcess(
                    argv, 0, self.identifier, ""
                )
            return self.run_docker(argv, root)

        return docker
