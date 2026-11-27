"""Fixture for native carrier Adapter tests."""

from hashlib import sha256
from pathlib import Path
import tempfile

from pydantic import BaseModel, ConfigDict, Field
import yaml


class NativeSelectionStub(BaseModel):
    """Return the selection fixture used by Project admission callers."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object] = Field(default_factory=dict)
    host_root: Path | None = None
    structure_snapshot: Path | None = None


class NativeCaptureFixture:
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        self.manifest = self.write(
            "AN-S-001-PROJECT_MANIFEST--manifest.md", "AN-S-001", "active", 1
        )
        self.selection = NativeSelectionStub(
            root=self.root,
            control_root=self.control,
            control_relative=self.control.relative_to(self.root),
            instance_id="a" * 64,
            project_name="Test",
            project_prefix="AN",
            manifest_path=self.manifest,
            manifest_ref="AN-S-001@1",
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
