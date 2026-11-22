"""Verify Git scope and changed-line filtering for EditorConfig Checker."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .. import source_line_length as lint


def finding(path, start, additional_lines=0):
    return {
        "location": {
            "path": path, "lines": {"begin": start, "end": additional_lines},
        },
        "description": "Line too long",
    }


class SourceLineLengthTests(unittest.TestCase):
    def test_project_switch_controls_the_cli(self):
        with TemporaryDirectory() as directory:
            config = Path(directory) / "pyproject.toml"
            argv = ["source_line_length.py", "--project-root", directory]
            with (
                patch.object(lint.sys, "argv", argv),
                patch.object(lint, "line_length_findings") as scan,
                redirect_stdout(StringIO()),
            ):
                config.write_text(
                    "[tool.anechoic.test_suite]\n"
                    "enforce_source_line_length = false\n",
                )
                self.assertEqual(lint.main(), 0)
                scan.assert_not_called()

                config.write_text(
                    "[tool.anechoic.test_suite]\n"
                    "enforce_source_line_length = true\n",
                )
                scan.return_value = [("RUNTIME_SETUP/new.py", 1, "Too long")]
                self.assertEqual(lint.main(), 1)
                scan.assert_called_once_with(Path(directory).resolve(), "HEAD")

    def test_reports_new_and_changed_lines_across_file_types(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lint.git(root, "init", "--quiet")
            (root / "RUNTIME_SETUP").mkdir()
            script = "RUNTIME_SETUP/start.py"
            old = "RUNTIME_SETUP/old.ts"
            renamed = "RUNTIME_SETUP/renamed file.ts"
            new = "RUNTIME_SETUP/panel.svelte"
            (root / script).write_text("legacy\nold\n")
            (root / old).write_text("unchanged\n")
            lint.git(root, "add", "--all")
            lint.git(
                root, "-c", "user.name=Test",
                "-c", "user.email=test@example.org",
                "commit", "--quiet", "-m", "Baseline",
            )
            lint.git(root, "mv", old, renamed)
            (root / script).write_text("inserted\nlegacy\nedited\n")
            lint.git(root, "add", script)
            (root / new).write_bytes(
                b"untracked\n<!-- " + lint.NEXT_LINE_DIRECTIVE + b" -->\n"
            )

            diagnostics = [
                finding(script, 1), finding(script, 2, 1),
                finding(renamed, 1), finding(new, 1),
            ]
            with patch.object(
                lint, "checker_findings", return_value=diagnostics,
            ):
                results = lint.line_length_findings(root, "HEAD")

            self.assertEqual(
                [(new, 1), (new, 2), (script, 1), (script, 3)],
                [(path, line) for path, line, _ in results],
            )
            self.assertIn(
                (new, 2, "Next-line suppression is disabled"), results,
            )

    def test_line_endings_do_not_create_changed_lines(self):
        self.assertEqual(
            {2}, lint.new_lines(b"old\r\nkeep\r\n", b"keep\nnew\n"),
        )
