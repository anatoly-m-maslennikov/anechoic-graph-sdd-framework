"""Fixture for native carrier Adapter tests."""

from hashlib import sha256
from pathlib import Path
import tempfile
from types import SimpleNamespace

import yaml


class NativeCaptureFixture:
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        self.manifest = self.write("AN-S-001-PROJECT_MANIFEST--manifest.md", "AN-S-001", "active", 1)
        self.selection = SimpleNamespace(root=self.root, control_root=self.control,
                                         manifest_path=self.manifest, project_prefix="AN",
                                         manifest_sha256=sha256(self.manifest.read_bytes()).hexdigest())

    def write(self, relative, atom_id, status, version, container=None):
        if "-T-" in atom_id and not relative.startswith("__TKT/"):
            relative = "__TKT/TASKS/" + relative
        path = self.control / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": atom_id}, "context": {"container": container or {"component": "C0"}},
                  "state": {"status": status, "version": version, "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n", encoding="utf-8")
        return path
