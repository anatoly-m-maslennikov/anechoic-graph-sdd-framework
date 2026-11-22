"""A native destination-create event can arrive before its source-remove event."""

from pathlib import Path
import re
import tempfile
import unittest

APP_ROOT = Path(__file__).resolve().parents[2]

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.scope_declaration_test_support__pub import write_scope_unit_declarations  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_reader import SourceReader  # noqa: E402
from KERNEL_MIXER_C59.relations import materialize  # noqa: E402


def write_settings(root: Path) -> Path:
    control = root / ".anechoic_anechoic"
    control.mkdir()
    (control / "anechoic_project_settings.toml").write_text(
        '[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n'
        '[paths]\ncontrol_root = ".anechoic_anechoic"\n',
        encoding="utf-8",
    )
    return control


def write_atom(path: Path, atom_id: str, *, status: str = "Active", version: int = 1) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f'atom_id: "{atom_id}"\nrole: "Requirement"\nform: "Definition"\n'
        f'status: "{status}"\nversion: {version}\n'
        'updated_at: "2026-11-04 00:00:00 +0000"\nsubjects: {}\nrelations: {}\n'
        "---\n# Summary\n\nFixture source.\n",
        encoding="utf-8",
    )
    return path


def source_path(declarations: dict, scope: str, role: str, name: str) -> Path:
    relative = Path(name)
    if not re.match(r"^[A-Za-z0-9_]+-[A-Z]-", relative.name):
        name = str(relative.with_name("CA-R-" + relative.name))
    return Path(declarations[scope]["authority_path"]) / role / name


class SourceMoveEventTests(unittest.TestCase):
    def test_batched_current_move_and_draft_removal_leave_no_stale_source_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            control = write_settings(root)
            declarations = write_scope_unit_declarations(root, (
                {"scope_unit_name": "MAIN"}, {"scope_unit_name": "TARGET"},
            ), control_root=control)
            current = source_path(declarations, "MAIN", "04_requirement", "current.md")
            draft = source_path(declarations, "MAIN", "04_requirement/draft", "draft.md")
            write_atom(current, "CA-R-424241")
            write_atom(draft, "CA-R-424242", status="Draft", version=2)
            reader = SourceReader(root)
            reader.capture()

            moved = source_path(declarations, "TARGET", "04_requirement", "moved.md")
            moved.parent.mkdir(parents=True, exist_ok=True)
            current.rename(moved)
            draft.unlink()
            rows, _ = reader.capture([
                {
                    "operation": "move", "old_path": current.relative_to(root).as_posix(),
                    "new_path": moved.relative_to(root).as_posix(),
                },
                {"operation": "remove", "old_path": draft.relative_to(root).as_posix(), "new_path": None},
            ])

            self.assertEqual([moved.relative_to(root).as_posix()], [
                row["source_path"] for row in rows if row["ref"] == "CA-R-424241"
            ])
            self.assertFalse(any(row["ref"] == "CA-R-424242@2-draft" for row in rows))
            self.assertIsNone(reader.capture_delta[draft.relative_to(root).as_posix()])

    def test_destination_event_prunes_missing_alias_but_not_real_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            control = write_settings(root)
            declarations = write_scope_unit_declarations(root, (
                {"scope_unit_name": "MAIN"}, {"scope_unit_name": "TARGET"},
            ), control_root=control)
            source = source_path(declarations, "MAIN", "04_requirement", "original.md")
            write_atom(source, "CA-R-424242")
            reader = SourceReader(root)
            reader.capture()
            target = source_path(declarations, "TARGET", "04_requirement", "moved.md")
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)
            rows, scopes = reader.capture([{
                "operation": "create", "old_path": None,
                "new_path": target.relative_to(root).as_posix(),
            }])
            matches = [row for row in rows if row["ref"] == "CA-R-424242"]
            self.assertEqual([target.relative_to(root).as_posix()], [row["source_path"] for row in matches])
            self.assertNotIn(source, reader._cached)
            self.assertNotIn(source, reader._source_paths)
            self.assertIsNone(reader.capture_delta[source.relative_to(root).as_posix()])
            self.assertIsNotNone(reader.capture_delta[target.relative_to(root).as_posix()])

            write_atom(source, "CA-R-424242")
            rows, _ = reader.capture([{
                "operation": "create", "old_path": None,
                "new_path": source.relative_to(root).as_posix(),
            }])
            rows, _ = materialize(rows, scopes)
            self.assertEqual(2, len([row for row in rows if row["ref"] == "CA-R-424242"]))
            self.assertEqual(2, len(reader._references.paths["CA-R-424242"]))


if __name__ == "__main__":
    unittest.main()
