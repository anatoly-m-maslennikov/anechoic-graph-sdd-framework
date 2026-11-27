from hashlib import sha256
from pathlib import Path
import sys
import tempfile

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / "IWE_CONSOLE_C43")]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import capture_native  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    NativeProjectSelection,
)


class NativeUpdateSupport:
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        (self.root / ".git").mkdir()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        manifest = self.write("AN-S-1-PROJECT_MANIFEST--manifest.md", "AN-S-1")
        self.path = self.write(
            "001_TICKETS/ASSETS/AN-T-1-ASSET--example.md", "AN-T-1"
        )
        self.selection = NativeProjectSelection(
            root=self.root,
            control_root=self.control,
            control_relative=self.control.relative_to(self.root),
            instance_id="a" * 64,
            project_name="Test",
            project_prefix="AN",
            manifest_path=manifest,
            manifest_ref="AN-S-1@1",
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        self.rows = capture_native(self.selection).atoms
        for row in self.rows:
            row["_source_sha256"] = sha256(
                (self.root / row["source_path"]).read_bytes()
            ).hexdigest()
        self.params = {
            "target": {"ref_id": "AN-T-1", "version": 1},
            "changes": {
                "body": "\n## Summary\n\nExample\n\n## Details\n\nNew\n"
            },
        }

    def write(self, name, identity, container=None):
        path = self.control / name
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "identity": {"atom_id": identity},
            "context": {"container": container or {"component": "C0"}},
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        path.write_text(
            "---\n"
            + yaml.safe_dump(header)
            + "---\n\n## Summary\n\nExample\n\n## Details\n\nOld\n"
        )
        return path
