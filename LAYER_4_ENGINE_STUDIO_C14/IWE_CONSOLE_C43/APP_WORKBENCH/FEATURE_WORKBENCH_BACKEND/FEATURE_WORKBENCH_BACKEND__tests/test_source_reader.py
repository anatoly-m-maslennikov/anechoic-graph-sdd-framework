from __future__ import annotations

from pathlib import Path
import unittest

import yaml

APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from KERNEL_MIXER_C59.public_rows import projected_rows  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import materialize  # noqa: E402
from KERNEL_MIXER_C59.header_columns import infer_header_schema  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_placement_audit import expected_carrier  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_reader import SourceReader  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.test_source_schema_audit import auditor  # noqa: E402


ATOM_COLUMNS = (
    "source_path", "status_group", "id", "ref", "version", "status",
    "current_scope_unit", "claim_target_scope_unit", "role", "form", "tier",
    "updated_at", "header_json", "_content_bytes", "content_properties_json",
    "relation_edges_json", "hash",
)
SCOPE_COLUMNS = (
    "name", "scope_unit_id", "parent_name", "declared_label", "ordered",
    "order_number", "declaration_source_path", "declaration_version",
    "relation_edges_json", "hash",
)
ROLES = (
    "01_concern", "02_analysis", "03_plan", "04_requirement", "05_method",
    "06_evaluation", "07_delivery", "08_implementation", "09_operations",
)


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


class SourceReaderTests(SourceReaderFixture, unittest.TestCase):
    @staticmethod
    def _relation_declarations():
        return [
            {
                "source_path": f"{reference}.md", "status_group": "Current",
                "id": reference, "ref": reference, "version": 1,
                "status": "Active", "role": "Requirement", "form": "Declaration",
                "tier": 1, "updated_at": None, "current_scope_unit": None,
                "claim_target_scope_unit": None, "header_json": {"relations": {},
                    "subjects": {"active": f"ANECHOIC_MODEL <+ CFEL <+ Relation//{name}"}},
                "content_markdown": (
                    "## Claim\n\n### Formal Claim\n\n```python\n"
                    f'subject_path(address="Relation//{name}")\n{binding}\n'
                    "```\n"
                ),
                "content_properties_json": [], "relation_edges_json": [], "hash": None,
            }
            for reference, name, binding in (
                ("CA-R-1", "IS_CONTAINED_BY",
                 'relation(source="Relation//IS_CONTAINED_BY", name="HAS_INVERSE", target="Relation//CONTAINS", reverse=False)'),
                ("CA-R-2", "CONTAINS", ""),
            )
        ]


    def _assert_root_container_case(self, root, relative, original, audit, non_root, index, field, stored, target):
        with self.subTest(field=field, index=index):
            text = original.replace("\nrole:", f"\n{field}role:", 1)
            root.write_text(text, encoding="utf-8")
            if index == 0:
                copy = root.parent / "z_copy" / root.name
                copy.parent.mkdir()
                copy.write_text(text, encoding="utf-8")
                atoms, scopes = self.reader.capture()
                copied = next(row for row in atoms if row["source_path"] == copy.relative_to(self.root).as_posix())
                self.assertNotIn("_project_root_header", copied)
            else:
                atoms, scopes = self.reader.capture([{"operation": "update", "new_path": relative}])
            source = next(row for row in atoms if row["source_path"] == relative)
            self.assertEqual("container" in source["header_json"], bool(field))
            self.assertEqual(source["header_json"].get("container"), stored)
            self.assertEqual(any(issue["field"] == "container" for issue in audit.issues(source)),
                             target is None)
            self.assertEqual(expected_carrier(source, {}, {}.get, None), (None, self.control.name))
            self.assertNotIn("_project_root_header", next(row for row in atoms if row["source_path"] == non_root))

            relation_declarations = self._relation_declarations()
            rows, scope_rows = materialize(relation_declarations + atoms, scopes)
            projected = next(row for row in rows if row["source_path"] == relative)
            direct = [edge["target_ref"] for edge in projected["relation_edges_json"]
                      if edge["relation_type"] == "IS_CONTAINED_BY"]
            self.assertEqual(direct, [] if target is None else [target])
            self.assertIs(projected["header_json"], source["header_json"])
            self.assertNotIn("_project_root_header", projected)
            self.assertEqual(len(scope_rows), 3)
            legacy_row = next(row for row in rows if row["ref"] == "CA-R-999")
            self.assertTrue(any(edge["target_ref"] == "MAIN" for edge in legacy_row["relation_edges_json"]))
            self.assertEqual(root.read_text(encoding="utf-8"), text)

        return atoms, rows, scope_rows


    def test_model_rows_do_not_restore_an_archived_declaration_from_a_copy(self) -> None:
        current = self._write_atom("MAIN", "04_requirement", "CA-R-900.md", atom_id="CA-R-900")
        archived = self._path("MAIN", "04_requirement", "CA-R-900@1.md", "099_archived")
        current.rename(archived)
        copied_row = {"id": "CA-R-900", "ref": "CA-R-900", "source_path": "installed/CA-R-900.md"}
        other_copy = {"id": "CA-R-901", "ref": "CA-R-901", "source_path": "installed/CA-R-901.md"}
        reader = SourceReader(self.root, include_archived=False)
        reader.capture()

        rows = reader.model_rows([copied_row, other_copy], lambda row: row["id"] in {"CA-R-900", "CA-R-901"})

        self.assertNotIn(copied_row, rows)
        self.assertIn(other_copy, rows)


    def test_real_root_child_inventory_includes_canonical_roles_and_declarations(self) -> None:
        for index, role in enumerate(ROLES, start=1):
            self._write_atom(
                "fixture", role, f"root-{index}.md", atom_id=f"CA-R-{100 + index}"
            )
        self._write_atom("CHILD", "04_requirement", "child.md", atom_id="CA-R-120")

        atoms, scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        self.assertEqual({row["name"] for row in scopes}, {"fixture", "MAIN", "CHILD"})
        self.assertEqual(len(scopes), len(self.declarations))
        self.assertTrue(
            {
                Path(row["declaration_path"]).relative_to(self.root).as_posix()
                for row in self.declarations.values()
            }
            <= {row["source_path"] for row in atoms}
        )
        role_paths = {
            Path(row["source_path"]).parts[-2]
            for row in atoms
            if Path(row["source_path"]).parts[-2] in ROLES
        }
        self.assertEqual(role_paths, set(ROLES))
        root_source = self.declarations["fixture"]["declaration_path"].relative_to(self.root).as_posix()
        for row in atoms:
            columns = (*ATOM_COLUMNS, "_project_root_header") if row["source_path"] == root_source else ATOM_COLUMNS
            self.assertEqual(tuple(row), columns)
        self.assertTrue(all(row["relation_edges_json"] == [] and row["hash"] is None for row in atoms))
        self.assertTrue(all(tuple(row) == SCOPE_COLUMNS for row in scopes))
        self.assertTrue(all(row["relation_edges_json"] == [] and row["hash"] is None for row in scopes))


    def test_root_container_default_changes_the_relation_and_preserves_stored_header(self) -> None:
        root = self.declarations["fixture"]["declaration_path"]
        relative = root.relative_to(self.root).as_posix()
        original = root.read_text(encoding="utf-8")
        original = original.replace("\nrole:", "\ncurrent_scope_unit: MAIN\nrole:", 1)
        audit = auditor(container_constraint=True)
        legacy = self._write_atom("MAIN", "04_requirement", "legacy.md", atom_id="CA-R-999")
        legacy.write_text(legacy.read_text().replace("\nrole:", "\ncurrent_scope_unit: MAIN\nrole:", 1))
        non_root = self.declarations["MAIN"]["declaration_path"].relative_to(self.root).as_posix()

        cases = (
            ("", None, "CA-SU--1"),
            ("container: {scope_unit: CA-SU--1}\n", {"scope_unit": "CA-SU--1"}, "CA-SU--1"),
            ("container: {scope_unit: CA-SU-00}\n", {"scope_unit": "CA-SU-00"}, "fixture"),
            ("container: null\n", None, None),
            ("container: {scope_unit: ''}\n", {"scope_unit": ""}, None),
            ("container: {atom: CA-R-1, scope_unit: CA-SU-00}\n",
             {"atom": "CA-R-1", "scope_unit": "CA-SU-00"}, None),
            ("", None, "CA-SU--1"),
        )
        for index, (field, stored, target) in enumerate(cases):
            atoms, rows, scope_rows = self._assert_root_container_case(
                root, relative, original, audit, non_root, index, field, stored, target)

        header = infer_header_schema(atoms)
        public_rows, _ = projected_rows(rows, scope_rows, header, self.reader.content_schema)
        public = next(row for row in public_rows if row["filename"] == root.name
                      and row["relative_path"] == self.control.name)
        self.assertNotIn("header.container.scope_unit", public)
        self.assertEqual(public["header.relations"]["IS_CONTAINED_BY"],
                         [{"kind": "Scope Unit", "reference": "CA-SU--1", "derived": False}])

        settings = self.control / "anechoic_project_settings.toml"
        settings_text = settings.read_text()
        for old, new in (('name = "fixture"', 'name = "different"'),
                         ('control_root = ".anechoic_anechoic"', 'control_root = ".anechoic_other"')):
            with self.subTest(settings=new):
                settings.write_text(settings_text.replace(old, new))
                atoms, _ = self.reader.capture()
                source = next(row for row in atoms if row["source_path"] == relative)
                self.assertNotIn("_project_root_header", source)
                self.assertEqual(yaml.safe_load(root.read_text().split("---", 2)[1]), source["header_json"])
                self.assertTrue(any(issue["field"] == "container" for issue in audit.issues(source)))


    def test_status_groups_refs_and_archive_locations(self) -> None:
        sources = {
            "CA-R-201": self._write_atom(
                "MAIN", "01_concern", "active.md", atom_id="CA-R-201", status="Active"
            ),
            "CA-R-202": self._write_atom(
                "MAIN", "02_analysis", "done.md", atom_id="CA-R-202", status="Done"
            ),
            "CA-R-203": self._write_atom(
                "MAIN", "03_plan", "canceled.md", atom_id="CA-R-203", status="Canceled"
            ),
            "CA-R-204@7-draft": self._write_atom(
                "MAIN", "04_requirement", "draft.md", atom_id="CA-R-204@7-draft",
                status="Draft", version=7, parts=("DRAFT",),
            ),
        }
        archived = (
            self._write_atom("MAIN", "05_method", "archived-folder.md", atom_id="CA-R-205", parts=("ARCHIVE",)),
            self._write_atom("MAIN", "06_evaluation", "archived-nested.md", atom_id="CA-R-206", parts=("nested", "Archived")),
            self._write_atom("MAIN", "07_delivery", "archived-status.md", atom_id="CA-R-207", status="archived"),
        )

        atoms, _scopes, stderr = self._capture()
        rows = {row["ref"]: row for row in atoms}

        self.assertEqual(stderr, "")
        self.assertEqual({ref: rows[ref]["status_group"] for ref in sources}, {
            "CA-R-201": "Current",
            "CA-R-202": "Current",
            "CA-R-203": "Current",
            "CA-R-204@7-draft": "Draft",
        })
        self.assertEqual(set(rows), set(sources) | {"CA-R-205@1", "CA-R-206@1", "CA-R-207@1"} |
                         {row["ref"] for row in atoms if row["form"] == "Scope Unit Declaration"})
        self.assertEqual(
            {row["source_path"] for row in atoms} & {
                path.relative_to(self.root).as_posix() for path in archived
            },
            {path.relative_to(self.root).as_posix() for path in archived},
        )
        self.assertTrue(all(rows[f"CA-R-{number}@1"]["status_group"] == "Archived"
                            for number in (205, 206, 207)))


    def test_archived_carrier_keeps_historical_header_and_content_shape(self) -> None:
        self._write_atom(
            "MAIN", "04_requirement", "CA-R-704-DECLARATION.md", atom_id="CA-R-704",
            form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Tier:: [int]{::1};
Atom.Content.Summary{::1}:: {::1};
```
""",
        )
        archived = self._write_atom(
            "MAIN", "04_requirement", "CA-R-705@2-old.md", atom_id="CA-R-705",
            status="Archived", version=2, parts=("archive",),
            body="## Summary\n\nFirst.\n\n## Summary\n\nSecond.\n",
        )
        archived.write_text(archived.read_text().replace("subjects: {}", "tier: principle\nsubjects: {}"))
        reader = SourceReader(self.root, schema_mode=1)
        rows, _ = reader.capture()
        row, = [row for row in rows if row["ref"] == "CA-R-705@2"]
        self.assertEqual("Archived", row["status_group"])
        self.assertEqual("principle", row["header_json"]["tier"])


    def test_implementation_role_accepts_current_and_draft_carriers(self) -> None:
        current = self._write_atom(
            "MAIN", "08_implementation", "CA-I-801-current.md", atom_id="CA-I-801",
        )
        draft = self._write_atom(
            "MAIN", "08_implementation", "CA-I-draft-next.md", atom_id="CA-I-draft",
            status="Draft", parts=("draft",),
        )

        atoms, _scopes, stderr = self._capture()
        by_path = {row["source_path"]: row for row in atoms}

        self.assertEqual("", stderr)
        self.assertEqual("Current", by_path[current.relative_to(self.root).as_posix()]["status_group"])
        self.assertEqual("Draft", by_path[draft.relative_to(self.root).as_posix()]["status_group"])


    def test_role_only_drafts_keep_distinct_technical_references(self) -> None:
        drafts = (
            self._write_atom(
                "MAIN", "09_operations", "CA-O-draft-first.md",
                atom_id="CA-O-draft", status="Draft", parts=("draft",),
            ),
            self._write_atom(
                "MAIN", "09_operations", "CA-O-draft-second.md",
                atom_id="CA-O-draft", status="Draft", parts=("draft",),
            ),
        )

        atoms, scopes, stderr = self._capture()
        rows = [row for row in atoms if row["source_path"] in {
            path.relative_to(self.root).as_posix() for path in drafts
        }]
        materialized, _scopes = materialize(atoms, scopes)

        self.assertEqual(stderr, "")
        self.assertEqual({row["ref"] for row in rows}, {
            f"CA-O-draft:{path.relative_to(self.root).as_posix()}" for path in drafts
        })
        self.assertEqual(
            {row["source_path"] for row in materialized} & {
                path.relative_to(self.root).as_posix() for path in drafts
            },
            {path.relative_to(self.root).as_posix() for path in drafts},
        )


    def test_other_project_and_legacy_role_markers_are_not_current_atom_filenames(self) -> None:
        legacy_concern = self._path("fixture", "01_concern", "ANECHOIC-CONC-004--legacy.md")
        legacy_concern.write_text(
            "---\natom_id: ANECHOIC-CONC-004\nversion: 1\n---\n# Legacy concern\n",
            encoding="utf-8",
        )
        legacy_analysis = self._path("fixture", "02_analysis", "ANECHOIC-ANRP-003--legacy.md")
        legacy_analysis.write_text(
            "---\natom_id: ANECHOIC-ANRP-003\nversion: 2\n---\n# Legacy analysis\n",
            encoding="utf-8",
        )
        draft = self._path("fixture", "04_requirement", "ANECHOIC-REQU-DRAFT--legacy.md", "drafts")
        draft.write_text("---\nversion: 1\n---\n# Legacy draft\n", encoding="utf-8")

        atoms, _scopes, stderr = self._capture()
        paths = {row["source_path"] for row in atoms}

        self.assertEqual(stderr, "")
        self.assertNotIn(legacy_concern.relative_to(self.root).as_posix(), paths)
        self.assertNotIn(legacy_analysis.relative_to(self.root).as_posix(), paths)
        self.assertNotIn(draft.relative_to(self.root).as_posix(), paths)



if __name__ == "__main__":
    unittest.main()
