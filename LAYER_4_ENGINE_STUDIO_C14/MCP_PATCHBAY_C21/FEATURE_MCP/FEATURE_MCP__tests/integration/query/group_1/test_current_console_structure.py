"""Run the console Structure SQL on the Current DuckDB owner."""

import json
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import monotonic, sleep
from unittest import TestCase

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner

from . import test_native_query_stdio as fixture
from ....native_query_test_support import STUDIO
from ....native_query_test_support import create_native_gateway


PROJECT = [
    "C00",
    None,
    "Component",
    "Anechoic",
    "Serve the project.",
    "AN-S-001@1",
    None,
]
COMPONENT = [
    "C2",
    "C00",
    "Component",
    "Service",
    "Provide a service.",
    "AN-S-002@2",
    "AN-S-004@3",
]
SEED = [
    "CS7",
    "C2",
    "Component Seed",
    "CS7",
    "Provide a seed.",
    "AN-S-003@4",
    "AN-S-003@4",
]


class CurrentConsoleStructureTest(TestCase):
    _write = fixture.NativeQueryStdioTests._write

    def setUp(self):
        fixture.NativeQueryStdioTests.setUp(self)
        self.control = self.root / fixture.CONTROL
        manifest = self.control / fixture.MANIFEST
        project = manifest.read_text().replace(
            "component: C0\n", "component: C00\n"
        )
        manifest.write_text(project + "\n## Purpose\n\nServe the project.\n")
        source = STUDIO / (
            "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/"
            "src/lib/console_structure.ts"
        )
        declaration = source.read_text().split("STRUCTURE_SQL =", 1)[1]
        self.sql = declaration.split("`")[1]

    def _component(self):
        self._write(
            "AN-S-002-SPEC-COMPONENT_MANIFEST--service.md",
            "AN-S-002",
            "active",
            2,
            template="component_manifest",
            tier=1,
            lens="SPEC",
            container={"component": "C00"},
            body="""
## Purpose

Provide a service.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C2', name='Service'))
```
""",
        )

    def _solution(self, index, target, *, tier=0, status="active", owner="C2"):
        ref = f"AN-S-{index:03}"
        path = f"SERVICE_C2/{ref}-DES-SOLUTION--service.md"
        if status == "draft":
            path = path.replace(f"/{ref}", f"/draft/{ref}@3-draft")
        self._write(
            path,
            ref,
            status,
            3,
            template="solution",
            tier=tier,
            lens="DES",
            container={"component": owner},
        )
        path = self.control / path
        source = path.read_text().replace(
            "\nstate:",
            f"\nrelations: {{ANSWERS: ['{target}']}}\nstate:",
            1,
        )
        path.write_text(source)
        return path

    def _snapshot(self):
        component_path = "AN-S-002-SPEC-COMPONENT_MANIFEST--service.md"
        seed_path = "SERVICE_C2/AN-S-003-SPEC-COMPONENT_SEED_MANIFEST--seed.md"
        purpose, solution = "Provide a seed.", "Handle a request."
        self._write(
            seed_path,
            "AN-S-003",
            "active",
            4,
            template="component_seed_manifest",
            tier=2,
            lens="SPEC",
            container={"component": "C2"},
            body=f"## Purpose\n\n{purpose}\n\n## Solution\n\n{solution}\n",
        )

        def carrier(ref, path):
            content = (self.control / path).read_bytes()
            return {
                "ref": ref,
                "source_path": path,
                "sha256": sha256(content).hexdigest(),
            }

        return {
            "model_sha256": "fixture",
            "project": carrier("AN-S-001@1", fixture.MANIFEST),
            "components": {
                "C2": {
                    **carrier("AN-S-002@2", component_path),
                    "parent": "C00",
                    "fields": {"name": "Service"},
                    "purpose": "Provide a service.",
                }
            },
            "packages": {
                "CS7": {
                    **carrier("AN-S-003@4", seed_path),
                    "component": "C2",
                    "fields": {"purpose": purpose, "solution": solution},
                }
            },
        }

    def _owner(self, snapshot: Path):
        base = fixture._native_inputs()

        def validate(fields, component):
            self.assertEqual("C00", component)
            identity = base.validate_manifest(fields, "C0")
            return replace(
                identity,
                parameters={
                    "runtime": {"iwe_console": {"import_graph": False}},
                },
            )

        inputs = replace(
            base,
            validate_manifest=validate,
            relation_types=base.relation_types | {"ANSWERS"},
        )
        gateway = create_native_gateway(self.root, fixture.CONTROL, inputs)
        selection = replace(gateway.selection, structure_snapshot=snapshot)
        owner = NativeQueryOwner(selection, inputs)
        self.addCleanup(owner.close)
        owner.start()
        return owner

    def _wait_rows(self, owner, expected):
        deadline = monotonic() + 6
        while True:
            rows = owner.run(self.sql, result_delivery="inline")["rows"]
            if sorted(rows) == expected or monotonic() >= deadline:
                self.assertEqual(expected, sorted(rows))
                return
            sleep(0.03)

    def test_exact_links_and_snapshot_updates_with_import_graph_disabled(self):
        self._component()
        active = self._solution(4, "AN-S-002@2")
        for index, target, options in (
            (5, "AN-S-002@1", {}),
            (6, "AN-S-002", {}),
            (7, "AN-S-002@2", {"tier": 1}),
            (8, "AN-S-002@2", {"status": "draft"}),
            (9, "AN-S-002@2", {"owner": "C00"}),
        ):
            self._solution(index, target, **options)

        snapshot = self.root / ".anechoic_tmp" / "structure.json"
        snapshot.parent.mkdir()
        structure = self._snapshot()
        snapshot.write_text(json.dumps(structure))
        owner = self._owner(snapshot)
        self.assertIn("component_seeds", owner.schema()["tables"])
        component, seed = COMPONENT.copy(), SEED.copy()
        self._wait_rows(owner, [PROJECT, component, seed])
        for reference in (component[-2], component[-1], seed[-1]):
            document = owner.atom_document(reference)
            self.assertEqual(reference, document["exact_ref"])

        edited = active.read_text().replace("AN-S-002@2", "AN-S-002@1")
        active.write_text(edited)
        component[-1] = None
        self._wait_rows(owner, [PROJECT, component, seed])

        structure["packages"]["CS7"]["fields"].pop("solution")
        pending = snapshot.with_suffix(".new")
        pending.write_text(json.dumps(structure))
        pending.replace(snapshot)
        seed[-1] = None
        self._wait_rows(owner, [PROJECT, component, seed])

        owner.close()
        structure["packages"].clear()
        snapshot.write_text(json.dumps(structure))
        reopened = self._owner(snapshot)
        self._wait_rows(reopened, [PROJECT, component])
