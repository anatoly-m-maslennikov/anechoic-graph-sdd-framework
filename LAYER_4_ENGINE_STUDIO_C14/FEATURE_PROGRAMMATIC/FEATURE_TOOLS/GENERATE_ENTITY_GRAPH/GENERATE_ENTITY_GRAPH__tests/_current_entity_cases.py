"""Additional current entity source cases."""

import hashlib
import json
from importlib import import_module
from unittest.mock import patch

_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
CEILINGS = _adapter.CEILINGS
read_current_carriers = _adapter.read_current_carriers


class CurrentEntityCases:
    def _preview_replacements(
        self,
    ):
        current, other, draft_paths, entries, manifest = self.prepare_preview()

        baseline = read_current_carriers(self.selected, self.repository)
        preview = read_current_carriers(
            self.selected, self.repository, model_draft_manifest=manifest
        )

        self.assertEqual(
            [current.stem, other.stem],
            [row["source"]["atom_id"] for row in baseline],
        )
        self.assertEqual(
            [other.stem, *(draft.stem for draft in draft_paths)],
            [row["source"]["atom_id"] for row in preview],
        )
        self.assertEqual(
            [draft.read_bytes() for draft in draft_paths],
            [row["raw"] for row in preview[1:]],
        )
        self.assertEqual(
            ["Draft", "Draft"],
            [row["read_view"]["status"] for row in preview[1:]],
        )
        entries[0]["source_sha256"] = "stale"
        manifest.write_text(json.dumps(entries))
        with self.assertRaisesRegex(
            ValueError, "predecessor is absent or has changed"
        ):
            read_current_carriers(
                self.selected, self.repository, model_draft_manifest=manifest
            )

    locals()[
        (
            "test_preview_replaces_a_pinned_curre"
            "nt_declaration_with_two_draft_sources"
        )
    ] = _preview_replacements

    def prepare_preview(self):
        current = self.write("CA-R-9001", "Original")
        other = self.write("CA-R-9002", "Unchanged")
        current.write_text(
            current.read_text().replace(
                "status: Active\n", "status: Active\nform: Declaration\n"
            )
        )
        draft_paths = [
            self.write(
                f"CA-R-900{number}",
                f"Replacement {number}",
                version=2,
                status="Draft",
                folder="000_draft",
            )
            for number in (3, 4)
        ]
        entries = []
        for draft in draft_paths:
            reference = f"{draft.stem}@2-draft"
            draft.write_text(
                draft.read_text().replace(
                    "status: Draft\n",
                    f"status: Draft\nform: Declaration\nref_id: {reference}\n",
                )
            )
            entries.append(
                {
                    "source": current.relative_to(self.repository).as_posix(),
                    "source_sha256": hashlib.sha256(
                        current.read_bytes()
                    ).hexdigest(),
                    "draft": draft.relative_to(self.repository).as_posix(),
                    "draft_ref": reference,
                }
            )
        manifest = self.repository / "preview.json"
        manifest.write_text(json.dumps(entries))

        return current, other, draft_paths, entries, manifest

    def test_reader_checks_existing_file_size_ceiling_before_parsing(self):
        self.write("CA-R-9001", "Too Large")

        with patch.dict(CEILINGS, {"max_file_bytes": 8}):
            with self.assertRaisesRegex(ValueError, "max_file_bytes ceiling"):
                read_current_carriers(self.selected, self.repository)

    def _live_edits(
        self,
    ):
        first = self.write("CA-R-9001", "Before", version=2)
        stale = self.repository / ".anechoic_anechoic/_projection/graph.json"
        stale.parent.mkdir(parents=True)
        stale.write_text("invalid stale snapshot", encoding="utf-8")
        self.assertEqual(
            {"Before"}, {row["identity"] for row in self.build()[0]["nodes"]}
        )
        self.write("CA-R-9001", "After", version=3)
        self.write("CA-R-9002", "New Entity", version=4)
        graph, provenance = self.build()
        self.assertEqual(
            {"After", "New Entity"},
            {row["identity"] for row in graph["nodes"]},
        )
        self.assertEqual(
            {("CA-R-9001", 3), ("CA-R-9002", 4)},
            {
                (row["source"]["atom_id"], row["source"]["version"])
                for row in provenance["owners"]
            },
        )
        first.unlink()
        graph, provenance = self.build()
        self.assertEqual(
            ["New Entity"], [row["identity"] for row in graph["nodes"]]
        )
        self.assertEqual(
            ["CA-R-9002"],
            [row["source"]["atom_id"] for row in provenance["owners"]],
        )
        self.assertEqual(
            "invalid stale snapshot", stale.read_text(encoding="utf-8")
        )

    locals()[
        (
            "test_live_edit_added_and_deleted_so"
            "urces_are_reflected_without_snapshot"
        )
    ] = _live_edits

    def _identical_subjects(
        self,
    ):
        paths = [
            self.write("CA-R-9001", "Shared"),
            self.write("CA-R-9002", "Shared", version=5),
        ]
        before = {path: path.read_bytes() for path in paths}
        graph, provenance = self.build()
        self.assertEqual(
            ["Shared"], [row["identity"] for row in graph["nodes"]]
        )
        self.assertNotIn("profile", graph["nodes"][0])
        self.assertEqual(2, len(graph["nodes"][0]["occurrence_ids"]))
        for owner in provenance["owners"]:
            source = owner["source"]
            path = self.repository / source["path"]
            self.assertEqual(
                hashlib.sha256(before[path]).hexdigest(), source["sha256"]
            )
        self.assertEqual(before, {path: path.read_bytes() for path in paths})

    locals()[
        (
            "test_identical_subject_identity_mer"
            "ges_and_keeps_all_current_provenance"
        )
    ] = _identical_subjects

    def _revision_names(
        self,
    ):
        canonical = self.write("CA-R-9001", "Revision Named", version=2)
        canonical.rename(self.selected / "CA-R-9001@2-current.md")
        self.write("OTHER-R-9002", "Other Project")
        (self.selected / "README.md").write_text(
            "# Ordinary documentation\n", encoding="utf-8"
        )
        (self.selected / "notes.md").write_text(
            "---\ntitle: Ordinary note\n---\n# Not an Atom\n", encoding="utf-8"
        )
        graph, provenance = self.build()
        self.assertEqual(
            {"Revision Named", "Other Project"},
            {node["identity"] for node in graph["nodes"]},
        )
        self.assertEqual(
            {("CA-R-9001", 2), ("OTHER-R-9002", 1)},
            {
                (owner["source"]["atom_id"], owner["source"]["version"])
                for owner in provenance["owners"]
            },
        )

    locals()[
        (
            "test_current_atom_discovery_accepts_r"
            "evision_names_and_declared_project_ids"
        )
    ] = _revision_names

    def test_source_selection_does_not_follow_symlink_into_outside_folder(
        self,
    ):
        self.write("CA-R-9001", "Selected")
        outside = self.write("CA-R-9002", "Outside", folder="../outside")
        (self.selected / "linked").symlink_to(
            outside.parent, target_is_directory=True
        )
        graph, provenance = self.build()
        self.assertEqual(
            ["Selected"], [node["identity"] for node in graph["nodes"]]
        )
        self.assertEqual(
            ["CA-R-9001"],
            [row["source"]["atom_id"] for row in provenance["owners"]],
        )

    def _qualified_endpoints(
        self,
    ):
        self.write(
            "CA-R-9001",
            "Artifact/Atom.Status: Active",
            dependencies=["Workflow.State"],
        )
        self.write("CA-R-9002", "Atom/Content Role: Plan")
        graph, _ = self.build()
        names = {node["id"]: node["identity"] for node in graph["nodes"]}
        actual = {
            (
                edge["kind"],
                names[edge["relation_source"]],
                names[edge["relation_target"]],
            )
            for edge in graph["edges"]
        }
        self.assertEqual(
            {
                ("NARROWER_THAN", "Artifact/Atom", "Artifact"),
                ("IS_PROPERTY_OF", "Artifact/Atom.Status", "Artifact/Atom"),
                (
                    "IS_ALLOWED_VALUE_OF",
                    "Artifact/Atom.Status:Active",
                    "Artifact/Atom.Status",
                ),
                ("IS_PROPERTY_OF", "Workflow.State", "Workflow"),
                ("NARROWER_THAN", "Atom/Content Role", "Atom"),
                (
                    "IS_ALLOWED_VALUE_OF",
                    "Atom/Content Role:Plan",
                    "Atom/Content Role",
                ),
            },
            actual,
        )
        self.assertIn("Atom/Content Role", names.values())

    locals()[
        (
            "test_subject_syntax_has_qualified_rel"
            "ation_endpoints_and_no_incidence_edges"
        )
    ] = _qualified_endpoints

    def test_malformed_subject_fails_without_guessed_nodes(self):
        self.write("CA-R-9001", "Atom///Broken")
        with self.assertRaisesRegex(ValueError, "Subject projection failed"):
            self.build()
