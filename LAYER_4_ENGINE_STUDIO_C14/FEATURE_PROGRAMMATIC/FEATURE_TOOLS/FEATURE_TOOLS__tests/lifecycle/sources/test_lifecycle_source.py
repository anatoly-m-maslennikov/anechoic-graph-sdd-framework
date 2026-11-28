from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources import (  # noqa: E402
    source__shared as source_module,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source__shared import (  # noqa: E402
    select_source,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source_binding import (  # noqa: E402
    SourceSelectionError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared import (  # noqa: E402
    resolve_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (  # noqa: E402
    write_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_model import (  # noqa: E402
    bind_placement,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.lifecycle.lifecycle_placement_test_support import (  # noqa: E402
    fixture_rules,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.lifecycle.sources import (  # noqa: E402
    _lifecycle_source_batch_cases as batch_cases,
    _lifecycle_source_query_cases as query_cases,
)

IndexedReader = query_cases.IndexedReader


class SourceTest(
    batch_cases.BatchCases, query_cases.QueryCases, unittest.TestCase
):
    def setUp(self):
        binding = bind_placement(fixture_rules())
        binding.__enter__()
        self.addCleanup(binding.__exit__, None, None, None)
        scratch = (
            TOOLS.parents[2]
            / ".anechoic_tmp"
            / "CA-P-2791"
            / "CA-P-2934"
            / "exact-carrier"
        )
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        (self.control / "anechoic_project_settings.toml").write_text(
            (
                '[project]\nname="TEST"\n[artifacts.identity]\n'
                'project_prefix="CA"\n[paths]\ncontrol_root=".'
                'anechoic_test"\n'
            )
        )
        write_scope_unit_declarations(self.root, control_root=self.control)
        self.folder = self.control / "04_requirement"
        self.folder.mkdir(exist_ok=True)
        self.selection = resolve_project(self.root)

    def carrier(
        self,
        name,
        *,
        identity="CA-R-10",
        version=1,
        status="Active",
        grouped=False,
        projection=False,
        folder=None,
    ):
        folder = folder or self.folder
        folder.mkdir(parents=True, exist_ok=True)
        if grouped:
            header = (
                "identity:\n  id: "
                f"{identity}"
                "\nstate:\n  version: "
                f"{version}"
                "\n  status: "
                f"{status}"
                "\n"
            )
        else:
            header = (
                f"atom_id: {identity}\nversion: {version}\nstatus: {status}\n"
            )
        if projection:
            header += "projection: {}\n"
        path = folder / name
        path.write_text(f"---\n{header}---\n\n## Summary\n\nExample\n")
        return path

    def test_current_and_pinned_state(self):
        path = self.carrier("CA-R-10-example.md", grouped=True, version=2)
        with patch.object(
            source_module,
            "read_scope_unit_declarations",
            wraps=source_module.read_scope_unit_declarations,
        ) as declarations:
            pin = select_source(self.selection, "CA-R-10")
        self.assertEqual(declarations.call_count, 1)
        self.assertEqual(
            (pin.path, pin.version, pin.sha256),
            (path, 2, hashlib.sha256(path.read_bytes()).hexdigest()),
        )
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10", expected_version=1)

    def test_draft_and_archived(self):
        self.carrier("CA-R-10@2-draft-example.md", version=2, status="draft")
        self.carrier(
            "CA-R-10-example@1.md", version=1, status="Archived", grouped=True
        )
        self.assertEqual(
            select_source(self.selection, "CA-R-10@2-draft").version, 2
        )
        self.assertEqual(
            select_source(self.selection, "CA-R-10@1").status, "Archived"
        )
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10")

    def test_ambiguity_projection_and_wrong_carrier(self):
        self.carrier("CA-R-10-first.md")
        self.carrier("CA-R-10-projection.md", projection=True)
        self.carrier("CA-R-10-copy.md", folder=self.root / "delivery")
        self.assertEqual(
            select_source(self.selection, "CA-R-10").path.name,
            "CA-R-10-first.md",
        )
        second = self.carrier("CA-R-10-second.md")
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10")
        second.unlink()
        self.carrier("CA-R-10-wrong.md", identity="CA-R-11")
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10")

    def test_leading_zero_atom_ids_are_distinct_and_select_exact_revisions(
        self,
    ):
        padded = self.carrier(
            "CA-R-096-EXAMPLE--example.md", identity="CA-R-096", version=25
        )
        unpadded = self.carrier(
            "CA-R-96-EXAMPLE--example.md", identity="CA-R-96", version=1
        )
        archived = self.carrier(
            "CA-R-096@24-EXAMPLE--example.md",
            identity="CA-R-096",
            version=24,
            status="Archived",
        )
        self.assertEqual(
            padded, select_source(self.selection, "CA-R-096").path
        )
        self.assertEqual(
            unpadded, select_source(self.selection, "CA-R-96").path
        )
        self.assertEqual(
            archived, select_source(self.selection, "CA-R-096@24").path
        )
        zero = self.carrier(
            "CA-R-000-EXAMPLE--example.md", identity="CA-R-000", version=1
        )
        self.assertEqual(zero, select_source(self.selection, "CA-R-000").path)
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-096@024")

    def test_project_prefix_and_root_local_authority(self):
        settings = self.control / "anechoic_project_settings.toml"
        settings.write_text(
            settings.read_text().replace(
                'project_prefix="CA"', 'project_prefix="DEMO"'
            )
        )
        selection = resolve_project(self.root)
        path = self.carrier(
            "DEMO-R-10-goal.md", identity="DEMO-R-10", folder=self.control
        )
        self.assertEqual(select_source(selection, "DEMO-R-10").path, path)
        archived = self.carrier(
            "DEMO-R-10@1-goal.md",
            identity="DEMO-R-10",
            status="archived",
            folder=self.folder / "archive",
        )
        draft = self.carrier(
            "DEMO-R-10@2-draft-goal.md",
            identity="DEMO-R-10",
            status="draft",
            version=2,
            folder=self.folder / "draft",
        )
        self.assertEqual(
            select_source(selection, "DEMO-R-10@1").path, archived
        )
        self.assertEqual(
            select_source(selection, "DEMO-R-10@2-draft").path, draft
        )
        with self.assertRaises(SourceSelectionError):
            select_source(selection, "CA-R-10")

    def test_grouped_and_separately_placed_workflow_steps(self):
        operations = self.control / "09_operations"
        workflow = operations / "CA-O-20-workflow"
        grouped = self.carrier(
            "CA-O-21-step.md",
            identity="CA-O-21",
            folder=workflow,
            grouped=True,
        )
        standalone = self.carrier(
            "CA-O-22-step.md", identity="CA-O-22", folder=operations
        )
        self.assertEqual(
            select_source(self.selection, "CA-O-21").path, grouped
        )
        self.assertEqual(
            select_source(self.selection, "CA-O-22").path, standalone
        )

    def test_currentness_is_scoped_to_identity(self):
        selected = self.carrier("CA-R-10-first.md")
        other = self.carrier("CA-R-11-before.md", identity="CA-R-11")
        original = source_module.parse_carrier

        def rename_unrelated(raw, path):
            other.rename(other.with_name("CA-R-11-after.md"))
            return original(raw, path)

        with patch.object(
            source_module, "parse_carrier", side_effect=rename_unrelated
        ):
            self.assertEqual(
                select_source(self.selection, "CA-R-10").path, selected
            )

        def add_duplicate(raw, path):
            self.carrier("CA-R-10-second.md")
            return original(raw, path)

        with patch.object(
            source_module, "parse_carrier", side_effect=add_duplicate
        ):
            with self.assertRaises(SourceSelectionError):
                select_source(self.selection, "CA-R-10")


if __name__ == "__main__":
    unittest.main()
