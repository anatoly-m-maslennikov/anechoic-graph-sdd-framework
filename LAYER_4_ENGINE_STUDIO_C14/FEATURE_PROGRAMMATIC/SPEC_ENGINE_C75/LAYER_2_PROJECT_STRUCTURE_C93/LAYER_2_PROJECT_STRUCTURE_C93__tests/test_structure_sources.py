import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext,
    canonical_native_header,
    native_header_view,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from ..LAYER_2_PROJECT_STRUCTURE_C93__rows import compile_structure_rows
from ..LAYER_2_PROJECT_STRUCTURE_C93__shared import compile_structure
from .structure_fixtures import (
    COMPONENT,
    CONTROL,
    LEGACY_COMPONENT,
    PROJECT,
    Model,
    StructureFixture,
    selection,
)


class StructureTests(StructureFixture, unittest.TestCase):
    def test_live_sources(self):
        result = compile_structure(selection(CONTROL), Model())
        self.assertTrue({"C14", "C59", "C62"} <= result["components"].keys())
        runtime = result["components"]["C62"]
        self.assertEqual(runtime["parent"], "C59")
        runtime_path = CONTROL / runtime["source_path"]
        runtime_header = native_header_view(
            parse_carrier(runtime_path.read_bytes(), runtime_path).metadata
        )
        self.assertEqual(
            runtime["ref"], f"AN-S-3088@{runtime_header['state']['version']}"
        )
        self.assertEqual(
            runtime["source_path"],
            "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/"
            "01_TIER_1_ARCHITECTURE/"
            "AN-S-3088-SPEC-COMPONENT_MANIFEST--declare-manifest-runtime.md",
        )
        self.assertEqual(
            runtime["sha256"],
            hashlib.sha256(runtime_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            result["project"]["ref"], selection(CONTROL).manifest_ref
        )
        self.assertEqual(
            result["project"]["sha256"], selection(CONTROL).manifest_sha256
        )
        self.assertEqual(result["components"]["C14"]["parent"], "C00")
        self.assertEqual(
            result["components"]["C14"]["source_path"],
            f"01_TIER_1_ARCHITECTURE/{COMPONENT.name}",
        )
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertEqual(result["packages"]["CS1"]["component"], "C50")
        seed = CONTROL / result["packages"]["CS1"]["source_path"]
        seed_header = native_header_view(
            parse_carrier(seed.read_bytes(), seed).metadata
        )
        self.assertEqual(
            result["packages"]["CS1"]["ref"],
            f"AN-S-3089@{seed_header['state']['version']}",
        )

    def _rows(self, root, project, child):
        rows = []
        for path in (project, child):
            raw = path.read_bytes()
            carrier = parse_carrier(raw, path)
            header = native_header_view(carrier.metadata)
            rows.append(
                {
                    "source_path": path.relative_to(root).as_posix(),
                    "exact_ref": (
                        f"{header['identity']['atom_id']}@"
                        f"{header['state']['version']}"
                    ),
                    "metadata": carrier.metadata,
                    "body": carrier.body,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
        return rows

    def test_ingested_rows_match_offline_and_enforce_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            control = root / "control"
            control.mkdir()
            project = root / PROJECT.name
            shutil.copyfile(PROJECT, project)
            child = control / COMPONENT.name
            child.write_text(LEGACY_COMPONENT)
            rows = self._rows(root, project, child)
            selected = selection(control, project)
            expected = compile_structure(selected, Model())
            project.unlink()
            child.unlink()
            args = (root, "control", selected.manifest_sha256, Model(), rows)
            self.assertEqual(
                expected,
                compile_structure_rows(*args, manifest_path=project.name),
            )
            for pin in ("", "0" * 64):
                with self.assertRaises(ValueError):
                    compile_structure_rows(root, "control", pin, Model(), rows)
            with self.assertRaises(ValueError):
                compile_structure_rows(
                    root,
                    "control",
                    selected.manifest_sha256,
                    Model(),
                    rows[1:],
                )
            with self.assertRaises(ValueError):
                compile_structure_rows(
                    root,
                    "control",
                    selected.manifest_sha256,
                    Model(),
                    rows,
                    manifest_path="foreign.md",
                )
            rows[0]["exact_ref"] = "AN-S-0@1"
            with self.assertRaises(ValueError):
                compile_structure_rows(
                    root, "control", selected.manifest_sha256, Model(), rows
                )

    def test_pin_duplicates_parent_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            shutil.copyfile(PROJECT, project)
            child.write_text(LEGACY_COMPONENT)
            (control / "__EXAMPLE_C14").mkdir()
            selected = selection(control)
            result = compile_structure(selected, Model())
            self.assertEqual(
                result["project"]["sha256"], selected.manifest_sha256
            )
            selected.manifest_ref = "AN-S-3037@99"
            with self.assertRaisesRegex(ValueError, "pin changed"):
                compile_structure(selected, Model())
            selected.manifest_ref = selection(control).manifest_ref
            duplicate = (
                control / "AN-S-4000-SPEC-PROJECT_MANIFEST--duplicate.md"
            )
            duplicate.write_text(
                project.read_text().replace("AN-S-3037", "AN-S-4000")
            )
            with self.assertRaisesRegex(ValueError, "exactly one"):
                compile_structure(selected, Model())
            duplicate.unlink()
            child.write_text(
                child.read_text().replace("component: C00", "component: C14")
            )
            with self.assertRaisesRegex(ValueError, "identity or parent"):
                compile_structure(selected, Model())
            child.write_text(LEGACY_COMPONENT)
            (control / "FIRST_C14").mkdir()
            (control / "SECOND_C14").mkdir()
            with self.assertRaisesRegex(
                ValueError, "Duplicate Component directory"
            ):
                compile_structure(selected, Model())
            (control / "FIRST_C14").rmdir()
            (control / "SECOND_C14").rmdir()

            class MutatingModel(Model):
                def validate_component_manifest(self, fields, parent_id):
                    child.write_text(child.read_text() + "\n")

            with self.assertRaisesRegex(ValueError, "changed"):
                compile_structure(selected, MutatingModel())

    def test_component_manifest_in_spec_and_duplicate_across_layouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            spec = control / "_SPEC"
            spec.mkdir()
            content = LEGACY_COMPONENT
            (spec / COMPONENT.name).write_text(content)
            result = compile_structure(selection(control), Model())
            self.assertEqual(
                result["components"]["C14"]["source_path"],
                f"_SPEC/{COMPONENT.name}",
            )
            (control / COMPONENT.name).write_text(content)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                compile_structure(selection(control), Model())

    def test_optional_carrier_directory_appearing_during_compilation(self):
        for name in ("_SPEC", "01_CUSTOM_ARCHITECTURE"):
            for symlink in (False, True):
                with (
                    self.subTest(name=name, symlink=symlink),
                    tempfile.TemporaryDirectory() as tmp,
                ):
                    control = Path(tmp).resolve() / "control"
                    control.mkdir()
                    project = control.parent / PROJECT.name
                    project.write_text(
                        PROJECT.read_text().replace(
                            "01_TIER_1_ARCHITECTURE",
                            "01_CUSTOM_ARCHITECTURE",
                            1,
                        )
                    )
                    selected = selection(control, project)
                    currentness = ReadContext.currentness

                    def mutate(
                        reader,
                        currentness=currentness,
                        control=control,
                        name=name,
                        symlink=symlink,
                    ):
                        result = currentness(reader)
                        directory = control / name
                        if symlink:
                            directory.symlink_to(control / "missing")
                        else:
                            directory.mkdir()
                            (directory / COMPONENT.name).write_text(
                                LEGACY_COMPONENT
                            )
                        return result

                    with (
                        patch.object(ReadContext, "currentness", mutate),
                        self.assertRaisesRegex(
                            ValueError, "Structure sources changed"
                        ),
                    ):
                        compile_structure(selected, Model())

    def test_canonical_component_classified_by_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            raw = COMPONENT.read_text()
            _, frontmatter, body = raw.split("---", 2)
            header = canonical_native_header(yaml.safe_load(frontmatter))
            header["tier"] = 1
            path = control / "AN-S-3039-SPEC-OTHER--engine.md"
            path.write_text(f"---\n{yaml.safe_dump(header)}---{body}")
            result = compile_structure(selection(control), Model())
            self.assertEqual(
                path.name, result["components"]["C14"]["source_path"]
            )
