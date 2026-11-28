"""Select active native Methodology Specs for Local Release."""

from hashlib import sha256
from pathlib import Path
import tempfile
from unittest.mock import NonCallableMock


class NativeReleaseSourcesFixture:
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.control = self.root / ".anechoic_fixture"
        self.ontology = self.control / "LAYER_1_META_ONTOLOGY_C9"
        manifest = self.control / "manifest.md"
        manifest.parent.mkdir()
        manifest.write_bytes(b"manifest")
        self.selection = NonCallableMock(
            spec_set=[
                "root",
                "control_root",
                "manifest_path",
                "manifest_sha256",
                "project_prefix",
                "parameters",
            ],
            root=self.root,
            control_root=self.control,
            manifest_path=manifest,
            manifest_sha256=sha256(b"manifest").hexdigest(),
            project_prefix="AN",
            parameters=None,
        )
        self.source = self.ontology / "__DES/__DOM/AN-S-1-DOM--current.md"
        self.carrier(self.source)

    def carrier(
        self,
        path,
        *,
        atom_id="AN-S-1",
        status="active",
        version=2,
        component="C9",
        template="",
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"""---
atom_family: SPEC
atom_id: {atom_id}
container:
  component: {component}
tier: 1
context:
  lens: DES/DOM
  template: {template}
state:
  status: {status}
  version: {version}
  updated_at: '2026-11-21T00:00:00Z'
---
## Summary

Native Spec.
""")

    def methodology_paths(self, c58, c72):
        paths = [
            (c58 / "__DES/AN-S-20-DES--method.md", "AN-S-20", "C58"),
            (self.control / "AN-S-21-SPEC--axiom.md", "AN-S-21", "C00"),
            (
                self.control / "_QA/AN-S-22-QA--project-goal-guidance.md",
                "AN-S-22",
                "C00",
            ),
            (
                self.control
                / "01_TIER_1_ARCHITECTURE/AN-S-29-SPEC--architecture.md",
                "AN-S-29",
                "C00",
            ),
            (
                self.control / "_DES/DOM/AN-S-30-DOM--design.md",
                "AN-S-30",
                "C00",
            ),
            (
                self.control / "_CUSTOM/AN-S-31-CUSTOM--custom.md",
                "AN-S-31",
                "C00",
            ),
            (
                c72 / "__DEVOPS/AN-S-23-DEVOPS--environment.md",
                "AN-S-23",
                "C72",
            ),
        ]
        return paths
