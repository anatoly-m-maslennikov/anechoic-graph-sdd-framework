from unittest.mock import NonCallableMock
from hashlib import sha256
import os
from pathlib import Path, PurePosixPath  # noqa: F401
from unittest.mock import patch  # noqa: F401
import tempfile
import unittest
import yaml

from .native_projection_relation_cases import NativeProjectionRelationCases
from .native_projection_delta_cases import NativeProjectionDeltaCases
from .native_projection_store_cases import NativeProjectionStoreCases

from KERNEL_MIXER_C59 import native_projection  # noqa: E402, F401
from KERNEL_MIXER_C59.native_projection import (
    project_native,  # noqa: F401
    project_native_delta,  # noqa: F401
)  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (  # noqa: E402
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.capture.capture__shared import (  # noqa: E402
    NativeCapture as NativeCapture,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402, F401


APP_ROOT = Path(__file__).resolve().parents[5]

EXTENSIONS = Path(
    os.environ.get(
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
        APP_ROOT.parents[1] / ".anechoic_tmp/workbench/extensions",
    )
)


class NativeProjectionTests(
    NativeProjectionRelationCases,
    NativeProjectionDeltaCases,
    NativeProjectionStoreCases,
    unittest.TestCase,
):
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        self.manifest = self.write(
            "AN-S-001-PROJECT_MANIFEST--manifest.md", "AN-S-001", "active", 1
        )
        self.selection = NonCallableMock(
            spec_set=[
                "root",
                "control_root",
                "manifest_path",
                "project_prefix",
                "manifest_sha256",
            ],
            root=self.root,
            control_root=self.control,
            manifest_path=self.manifest,
            project_prefix="AN",
            manifest_sha256=sha256(self.manifest.read_bytes()).hexdigest(),
        )

    def write(self, relative, atom_id, status, version, container=None):
        if "-T-" in atom_id and not relative.startswith("__TKT/"):
            relative = "__TKT/TASKS/" + relative
        path = self.control / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "identity": {"atom_id": atom_id},
            "context": {"container": container or {"component": "C0"}},
            "state": {
                "status": status,
                "version": version,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        path.write_text(
            "---\n"
            + yaml.safe_dump(header)
            + "---\n\n## Summary\n\nExample\n",
            encoding="utf-8",
        )
        return path

    def test_publishes_admitted_rows_with_invalid_source_carriers(self):
        bad = self.write("AN-T-09--task.md", "AN-T-09", "invalid", 1)
        capture = capture_native(self.selection)
        self.assertIn(bad.relative_to(self.root).as_posix(), capture.errors)
        store = QueryStore(extension_directory=EXTENSIONS, native=True)
        self.addCleanup(store.close)
        project_native(
            store,
            capture,
            relation_types={"CONTAINED_BY", "CONTAINS"},
            inverses={"CONTAINED_BY": "CONTAINS"},
        )
        self.assertEqual(
            [["AN-S-001"]],
            store.run("SELECT reference FROM atoms")["rows"],
        )
