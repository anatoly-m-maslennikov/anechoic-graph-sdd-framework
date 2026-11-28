from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[3]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure_snapshot__pub import (
    parse_structure,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    NativeProjectSelection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


def collide_first_two_links(attempts):
    link = os.link

    def collide(source, filename, **options):
        attempts.append(filename)
        if len(attempts) <= 2:
            mode = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            with os.fdopen(
                os.open(filename, mode, 0o600, dir_fd=options["dst_dir_fd"]),
                "wb",
            ) as occupied:
                occupied.write(b"occupied")
        return link(source, filename, **options)

    return collide


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.native.drafts import (  # noqa: E402
    _native_draft_cases_1 as cases1,
    _native_draft_cases_2 as cases2,
)


class NativeDraftTests(
    cases1.NativeDraftCases1, cases2.NativeDraftCases2, unittest.TestCase
):
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        (self.root / ".git").mkdir()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        manifest = self.write("AN-S-1-PROJECT_MANIFEST--manifest.md", "AN-S-1")
        self.path = self.write(
            "001_TICKETS/TASKS/AN-T-1-TASK--example.md", "AN-T-1"
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
        self.params = {
            "sourceCurrent": {"ref_id": "AN-T-1", "version": 1},
            "changes": {
                "body": "\n# Summary\n\nExample\n\n## Details\n\nNew\n"
            },
        }

    def write(
        self, name, identity, *, version=1, status="active", template="task"
    ):
        path = self.control / name
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "identity": {"atom_id": identity},
            "context": {
                "container": {"component": "C0"},
                "template": template,
            },
            "state": {
                "status": status,
                "version": version,
                "updated_at": "2026-01-01",
            },
        }
        path.write_text(
            "---\n"
            + yaml.safe_dump(header)
            + "---\n\n# Summary\n\nExample\n\n## Details\n\nOld\n"
        )
        return path

    def test_indexed_max_and_real_collision_retries(self):
        from unittest.mock import Mock, patch

        capture = capture_native(self.selection)
        indexed = Mock(atoms=capture.atoms, errors=[], max_archived_version=7)
        attempts = []
        directory = self.path.parent / "01_draft"
        directory.mkdir()

        with (
            patch(
                (
                    'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared.revalidate_native'
                ),
                return_value=indexed,
            ),
            patch("os.link", side_effect=collide_first_two_links(attempts)),
        ):
            result = create_draft(
                self.selection, self.params, current_rows=self.rows
            )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("AN-T-1@10-draft", result["savedDraft"]["ref_id"])
        self.assertEqual(3, len(attempts))
        self.assertEqual(
            [b"occupied", b"occupied"],
            [(directory / name).read_bytes() for name in attempts[:2]],
        )


class NativeRevisionCarrierTests:
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        manifest = self.selection.manifest_path
        manifest.write_text("""---
identity: {atom_id: AN-S-1}
context: {container: {component: C0}, tier: -1, lens: SPEC, template: project_manifest}
state: {status: active, version: 1}
---
## Summary

Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Test', prefix='AN', lens_whitelist=['DES', 'SPEC']))
```
""")
        self.selection = replace(
            self.selection,
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )

    def spec(self, name, atom_id, lens="DES", component="C9"):
        path = self.write(name, atom_id)
        header, body = path.read_text().split("---\n", 2)[1:]
        data = yaml.safe_load(header)
        data["context"] = {"container": {"component": component}, "lens": lens}
        path.write_text("---\n" + yaml.safe_dump(data) + "---\n" + body)
        return path


class NewNativeTaskTests:
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        self.new = {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": "\n## Summary\n\nCreate a Task!\n\n## Work\n\nDo it.\n",
            }
        }


class NativePromotionTests:
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        output = create_draft(
            self.selection, self.params, current_rows=self.rows
        )
        self.draft = self.root / output["savedDraft"]["path"]
        self.rows = capture_native(self.selection).atoms
        self.promotion = {
            "target": {"ref_id": "AN-T-1@2-draft", "version": 2},
            "targetStatus": "active",
        }


class ComponentContractLifecycleTests:
    write = NativeDraftTests.write

    spec = NativeRevisionCarrierTests.spec

    def setUp(self):
        NativeRevisionCarrierTests.setUp(self)
        manifest = self.selection.manifest_path
        manifest.write_text(
            manifest.read_text().replace("component: C0}", "component: C00}")
        )
        self.selection = replace(
            self.selection,
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        declaration = self.spec(
            "AN-S-2-SPEC--component.md", "AN-S-2", lens="SPEC", component="C0"
        )
        self.spec("UNIT_C9/__DES/AN-S-4-DES--example.md", "AN-S-4")
        self.snapshot = self._component_snapshot(manifest, declaration)
        self.record = self.snapshot.components["C9"]
        self.body = (
            "\n## Summary\n\nImport graph contract\n\n## Guarantee\n\nThe "
            "graph includes imports.\n"
        )
        self.new = {
            "newAtom": {
                "template": "component_contract",
                "container": {"component": "C9"},
                "lens": "DES",
                "body": self.body,
            }
        }

    def _component_snapshot(self, manifest, declaration):
        return parse_structure(
            json.dumps(
                {
                    "model_sha256": "model",
                    "project": {
                        "ref": "AN-S-1@1",
                        "sha256": sha256(manifest.read_bytes()).hexdigest(),
                    },
                    "components": {
                        "C9": {
                            "parent": "C00",
                            "ref": "AN-S-2@1",
                            "sha256": sha256(
                                declaration.read_bytes()
                            ).hexdigest(),
                            "fields": {"name": "Unit", "lens_whitelist": None},
                            "source_path": declaration.relative_to(
                                self.control
                            ).as_posix(),
                        }
                    },
                    "packages": {},
                }
            ).encode()
        )

    def create(self):
        return create_draft(
            self.selection,
            self.new,
            current_rows=capture_native(self.selection).atoms,
            structure_snapshot=self.snapshot,
        )

    def promote(self, ref, version):
        return promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": version},
                "targetStatus": "ready",
            },
            current_rows=capture_native(self.selection).atoms,
            structure_snapshot=self.snapshot,
        )
