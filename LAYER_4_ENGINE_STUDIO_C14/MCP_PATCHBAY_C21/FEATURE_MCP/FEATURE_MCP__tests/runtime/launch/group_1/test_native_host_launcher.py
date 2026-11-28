"""Native Project startup keeps the host identity and Manifest port."""

from pathlib import Path
from dataclasses import replace
import shutil
import tempfile
import unittest
from unittest.mock import patch

import yaml

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    ProjectAdmissionError,
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project__shared import (
    Launcher,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    backend__shared import (
    ProjectMcpBackend,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    transport_support__shared import (
    native_arguments,
)
from ..group_2.launcher_startup_test_support import Backend
from ..group_2.launcher_startup_test_support import healthy_row

MCP = Path(__file__).resolve().parents[4]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"


class HostBackend(Backend):
    def start(self, selection, image_id, fingerprint, timeout, port=None):
        super().start(selection, image_id, fingerprint, timeout, port)
        self.rows = [
            healthy_row(project=selection.instance_id, host_port=str(port))
        ]


class NativeHostLauncherTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.control = self.root / ".anechoic_anechoic"
        path = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
        path.parent.mkdir(parents=True)
        header = {
            "identity": {"atom_id": "AN-S-001"},
            "context": {
                "container": {"component": "C00"},
                "tier": -1,
                "template": "project_manifest",
            },
            "state": {"status": "active", "version": 1},
        }
        path.write_text(
            f"---\n{yaml.safe_dump(header)}---\n\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            'declare_entity(entity_name="Project Manifest", '
            'instance=ProjectManifest(name="Anechoic", prefix="AN", '
            'parameters={"project_mcp": {"http_port": 56318}}))\n```\n',
            encoding="utf-8",
        )

    def test_launcher_selects_manifest_and_publishes_its_port(self):
        backend = HostBackend()
        result = Launcher(backend=backend).launch(
            self.root, source_root=PROGRAMMATIC
        )
        selected = select_runtime_project(self.root)
        self.assertEqual(
            ("READY_STARTED", 56318, str(self.control), selected.instance_id),
            (
                result["condition"],
                result["port"],
                result["control_root"],
                result["project_id"],
            ),
        )
        self.assertEqual([56318], backend.start_ports)
        self.assertEqual(
            "anechoic-mcp-" + selected.instance_id[:24],
            ProjectMcpBackend._compose_project(selected),
        )
        environment = ProjectMcpBackend._environment(
            selected, result["image_id"], result["fingerprint"], 56318
        )
        self.assertEqual(
            (str(self.root), self.control.name, selected.instance_id, "56318"),
            (
                environment["ANECHOIC_PROJECT_ROOT"],
                environment["ANECHOIC_CONTROL_ROOT"],
                environment["ANECHOIC_PROJECT_INSTANCE_ID"],
                environment["ANECHOIC_MCP_HTTP_PORT"],
            ),
        )
        refused = Launcher(backend=backend).launch(
            self.root, source_root=PROGRAMMATIC, port=56317
        )
        self.assertEqual("PROJECT_SELECTION_REFUSED", refused["condition"])
        self.assertEqual(1, backend.start_calls)

    def test_invalid_manifest_port_refuses_before_runtime_effects(self):
        selection = select_runtime_project(self.root)
        for port in (None, True, 0, 65536, "56318"):
            with self.subTest(port=port):
                backend = Backend()
                invalid = replace(
                    selection, parameters={"project_mcp": {"http_port": port}}
                )
                with patch(
                    (
                        "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launc"
                        "her.resolve_project"
                    ),
                    return_value=invalid,
                ):
                    result = Launcher(backend=backend).launch(
                        self.root, source_root=PROGRAMMATIC
                    )
                self.assertEqual(
                    "PROJECT_SELECTION_REFUSED", result["condition"]
                )
                self.assertEqual(
                    (0, 0), (backend.resolve_image_calls, backend.start_calls)
                )

    def test_transport_checks_identity_and_accepts_only_bound_roots(self):
        host = (
            Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
            / "host-project"
        )
        shutil.copytree(self.control, host / self.control.name)
        identity = select_runtime_project(host).instance_id
        host.rename(host.with_name("detached-project"))
        transported = select_runtime_project(
            self.root, instance_id=identity, host_root=host
        )
        for root in (self.root, host):
            self.assertEqual(
                {"sql": "select 1"},
                native_arguments(
                    {"project_root": str(root), "sql": "select 1"},
                    transported,
                    self.root,
                ),
            )
        with self.assertRaises(ValueError):
            native_arguments(
                {"project_root": str(host.parent)}, transported, self.root
            )
        with self.assertRaises(ProjectAdmissionError):
            select_runtime_project(
                self.root, instance_id="a" * 64, host_root=host
            )
        host.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ProjectAdmissionError):
            select_runtime_project(
                self.root, instance_id=identity, host_root=host
            )


if __name__ == "__main__":
    unittest.main()
