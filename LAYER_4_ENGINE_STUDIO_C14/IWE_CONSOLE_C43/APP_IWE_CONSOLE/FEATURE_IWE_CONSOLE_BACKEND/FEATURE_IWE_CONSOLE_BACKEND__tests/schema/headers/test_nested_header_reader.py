"""Nested Header reading stays source-faithful and graph-compatible."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock  # noqa: F401


from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    write_scope_unit_declarations,
)  # noqa: E402
from KERNEL_MIXER_C59 import content_schema as content_schema_module  # noqa: F401
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import materialize  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (
    SourceReader,
)  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.watch.source_watcher__pub import (
    SourceWatcher,
)  # noqa: E402


from .nested_content_schema_cases import NestedContentSchemaCases


APP_ROOT = Path(__file__).resolve().parents[5]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

SUMMARY_RULE = (
    'property_rule(address="Atom.Content.Summary", occurrences="1", '
    'values="1")'
)


def write_settings(root: Path) -> Path:
    control = root / ".anechoic_anechoic"
    control.mkdir()
    (control / "anechoic_project_settings.toml").write_text(
        '[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n'
        '[paths]\ncontrol_root = ".anechoic_anechoic"\n',
        encoding="utf-8",
    )
    return control


class NestedHeaderReaderTests(NestedContentSchemaCases, unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.control = write_settings(self.root)
        self.declarations = write_scope_unit_declarations(
            self.root,
            ({"scope_unit_name": "MAIN", "scope_unit_label": "LAYER"},),
            control_root=self.control,
        )
        self.reader = SourceReader(self.root)

    def _path(self, name: str) -> Path:
        name = "CA-R-" + name
        path = (
            Path(self.declarations["MAIN"]["authority_path"])
            / "04_requirement"
            / name
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _nested(
        self,
        name: str,
        atom_id: str,
        *,
        form: str = "Definition",
        container: str | None = None,
        container_kind: str = "scope_unit",
        topic: str | None = None,
        body: str = "# Summary\n\nNested source.\n",
    ) -> Path:
        context = "  role: Requirement\n  form: " + form + "\n  tier: 2\n"
        if container is not None:
            context = (
                f"  container:\n    {container_kind}: {container}\n" + context
            )
        if topic is not None:
            context += (
                f"  topics:\n    main_subject: {topic}\n    dependencies: []\n"
            )
        path = self._path(name)
        path.write_text(
            "---\n"
            f"identity:\n  atom_id: {atom_id}\n  ref_id: {atom_id}\n"
            f"context:\n{context}"
            "relations: {}\n"
            "state:\n  status: Active\n  version: 3\n"
            '  updated_at: "2026-11-06 12:00:00 +0400"\n'
            "destination:\n  file:\n"
            f"    name: {Path(name).name}\n    path: current\n"
            "---\n" + body,
            encoding="utf-8",
        )
        return path

    def _model_declaration(
        self, name: str, atom_id: str, statement: str
    ) -> Path:
        return self._nested(
            name,
            atom_id,
            form="Declaration",
            body=(
                "## Claim\n\n### Formal Claim\n\n```python\n"
                f"{statement}"
                "\n```\n"
            ),
        )

    def test_nested_and_flat_headers_keep_typed_values_and_raw_properties(
        self,
    ) -> None:
        nested = self._nested(
            "nested.md", "CA-R-101", topic="Subject/Graph/Node"
        )
        flat = self._path("flat.md")
        flat.write_text(
            "---\natom_id: CA-R-102\nrole: Requirement\nform: Definition\n"
            "status: Active\nversion: 2\ntier: 1\nsubjects: {}\nrelations: {}\n---\n# Summary\n\nFlat.\n",
            encoding="utf-8",
        )

        atoms, _scopes = self.reader.capture()
        by_id = {row["id"]: row for row in atoms}

        self.assertEqual(
            (
                "CA-R-101",
                "CA-R-101",
                3,
                "Active",
                "Requirement",
                "Definition",
                2,
            ),
            tuple(
                by_id["CA-R-101"][name]
                for name in (
                    "id",
                    "ref",
                    "version",
                    "status",
                    "role",
                    "form",
                    "tier",
                )
            ),
        )
        self._assert_nested_header(by_id, nested)

    def _assert_nested_header(self, by_id, nested):
        self.assertNotIn("atom_id", by_id["CA-R-101"]["header_json"])
        self.assertEqual(
            "CA-R-101", by_id["CA-R-101"]["header_json"]["identity"]["atom_id"]
        )
        self.assertEqual("CA-R-102", by_id["CA-R-102"]["id"])
        self.assertEqual(
            nested.relative_to(self.root).as_posix(),
            by_id["CA-R-101"]["source_path"],
        )

    def test_nested_identity_id_is_read_without_rewriting_the_raw_header(
        self,
    ) -> None:
        source = self._path("identity-id.md")
        source.write_text(
            "---\n"
            "identity:\n  id: CA-R-103\n  ref_id: CA-R-103\n"
            "context:\n  role: Requirement\n  form: Definition\n  tier: 2\n"
            "relations: {}\n"
            "state:\n  status: Active\n  version: 3\n"
            "destination:\n  file:\n    name: identity-id.md\n    path: current\n"
            "---\n# Summary\n\nNested source.\n",
            encoding="utf-8",
        )

        atoms, _scopes = self.reader.capture()
        row = next(item for item in atoms if item["id"] == "CA-R-103")

        self.assertEqual(("CA-R-103", "CA-R-103"), (row["id"], row["ref"]))
        self.assertEqual("CA-R-103", row["header_json"]["identity"]["id"])
        self.assertNotIn("atom_id", row["header_json"]["identity"])

    def test_nested_topics_and_containers_make_direct_and_derived_graph_facts(
        self,
    ) -> None:
        self._nested(
            "contained-by.md",
            "CA-R-201",
            form="Relation Definition",
            topic="Subject/Graph/Relation//IS_CONTAINED_BY",
            body=(
                "## Claim\n\n### Formal Claim\n\n```python\n"
                'relation(source="Relation//IS_CONTAINED_BY", '
                'name="HAS_INVERSE", target="Relation//CONTAINS")\n```\n'
            ),
        )
        self._nested(
            "contains.md",
            "CA-R-202",
            form="Relation Definition",
            topic="Subject/Graph/Relation//CONTAINS",
        )
        self._nested("parent.md", "CA-R-203", container="TEST-SU-1")
        self._nested(
            "child.md", "CA-R-204", container="CA-R-203", container_kind="atom"
        )

        atoms, scopes = materialize(*self.reader.capture())
        by_ref = {row["ref"]: row for row in atoms}
        by_scope = {row["name"]: row for row in scopes}

        self._assert_graph_edges(by_ref, by_scope)

    def _assert_graph_edges(self, by_ref, by_scope):
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-R-203",
                "target_kind": "Scope Unit",
                "target_ref": "MAIN",
                "relation_type": "IS_CONTAINED_BY",
                "derived": False,
            },
            by_ref["CA-R-203"]["relation_edges_json"],
        )
        self.assertIn(
            {
                "source_kind": "Scope Unit",
                "source_ref": "MAIN",
                "target_kind": "Atom",
                "target_ref": "CA-R-203",
                "relation_type": "CONTAINS",
                "derived": True,
            },
            by_scope["MAIN"]["relation_edges_json"],
        )
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-R-204",
                "target_kind": "Atom",
                "target_ref": "CA-R-203",
                "relation_type": "IS_CONTAINED_BY",
                "derived": False,
            },
            by_ref["CA-R-204"]["relation_edges_json"],
        )
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-R-203",
                "target_kind": "Atom",
                "target_ref": "CA-R-204",
                "relation_type": "CONTAINS",
                "derived": True,
            },
            by_ref["CA-R-203"]["relation_edges_json"],
        )

    def test_declaration_directory_move_rebuilds_scope_inventory(self) -> None:
        self.reader.capture()
        directory = Path(self.declarations["MAIN"]["declaration_path"]).parent
        moved = self.control / "moved-declarations"
        directory.rename(moved)

        _atoms, scopes = self.reader.capture(
            [
                {
                    "operation": "move",
                    "old_path": directory.relative_to(self.root).as_posix(),
                    "new_path": moved.relative_to(self.root).as_posix(),
                }
            ]
        )

        self.assertEqual(["fixture"], [row["name"] for row in scopes])

    def test_lexical_symlink_replacement_removes_cached_source(self) -> None:
        source = self._nested("replace-me.md", "CA-R-301")
        self.reader.capture()
        outside = self.root / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        source.unlink()
        source.symlink_to(outside)

        atoms, _scopes = self.reader.capture(
            [
                {
                    "operation": "update",
                    "old_path": None,
                    "new_path": source.relative_to(self.root).as_posix(),
                }
            ]
        )
        watcher = SourceWatcher(self.root, self.control)

        self.assertNotIn("CA-R-301", {row["id"] for row in atoms})
        self.assertEqual(
            source.relative_to(self.root).as_posix(),
            watcher._relative(str(source)),
        )
        self.assertIsNone(
            watcher._relative(str(self.control / ".." / "outside.md"))
        )

    def test_symlinked_parent_replacement_removes_cached_source(self) -> None:
        source = self._nested("linked/escaped.md", "CA-R-302")
        self.reader.capture()
        outside = self.root / "outside"
        source.parent.rename(outside)
        source.parent.symlink_to(outside, target_is_directory=True)

        atoms, _scopes = self.reader.capture(
            [
                {
                    "operation": "update",
                    "old_path": None,
                    "new_path": source.relative_to(self.root).as_posix(),
                }
            ]
        )

        self.assertNotIn("CA-R-302", {row["id"] for row in atoms})


if __name__ == "__main__":
    unittest.main()
