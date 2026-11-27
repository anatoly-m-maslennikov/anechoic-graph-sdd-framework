"""Verify Git scope and changed-line filtering for EditorConfig Checker."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    source_line_length as lint,
)


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

                config = (
                    Path(directory)
                    / (
                        'LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/py'
                        'project.toml'
                    )
                )
                config.parent.mkdir(parents=True)
                config.write_text(
                    "[tool.anechoic.test_suite]\n"
                    "enforce_source_line_length = true\n",
                )
                scan.return_value = [
                    ("LAYER_5_USER_SETUP_C65/new.py", 1, "Too long")
                ]
                self.assertEqual(lint.main(), 1)
                scan.assert_called_once_with(Path(directory).resolve(), "HEAD")

    def test_reports_new_and_changed_lines_across_file_types(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lint.git(root, "init", "--quiet")
            (root / "LAYER_5_USER_SETUP_C65").mkdir()
            script = "LAYER_5_USER_SETUP_C65/start.py"
            old = "LAYER_5_USER_SETUP_C65/old.ts"
            renamed = "LAYER_5_USER_SETUP_C65/renamed file.ts"
            new = "LAYER_5_USER_SETUP_C65/panel.svelte"
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

    def test_static_checks_all_covered_files_and_reports_tool_errors(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            lint.git(root, "init", "--quiet")
            config = root / "pyproject.toml"
            config.write_text(
                "[tool.anechoic.test_suite]\n"
                "enforce_source_line_length = true\n",
            )
            (root / ".editorconfig").write_text("root = true\n")
            path = root / "LAYER_3_DEVOPS_C80/example.tsx"
            path.parent.mkdir()
            path.write_text("x" * 80 + "\n")
            with (
                patch.object(
                    lint,
                    "checker_findings",
                    return_value=[
                        finding("LAYER_3_DEVOPS_C80/example.tsx", 1),
                    ],
                ) as checker,
                redirect_stdout(StringIO()),
            ):
                self.assertEqual(lint.check(root), 1)
                self.assertIn(
                    "LAYER_3_DEVOPS_C80/example.tsx", checker.call_args[0][1]
                )
            with patch.object(
                lint, "checker_findings", side_effect=ValueError("broken")
            ):
                self.assertEqual(lint.check(root), 2)

    def test_real_checker_counts_characters(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".editorconfig").write_text(
                "root = true\n\n[*.py]\nmax_line_length = 79\n",
            )
            (root / "example.py").write_text(
                "\n".join(["x" * 79, "x" * 80, "é" * 79, "é" * 80])
                + "\n",
                encoding="utf-8",
            )
            results = lint.checker_findings(root, ["example.py"])
            self.assertEqual(
                [2, 4],
                [item["location"]["lines"]["begin"] for item in results],
            )

    def test_line_endings_do_not_create_changed_lines(self):
        self.assertEqual(
            {2}, lint.new_lines(b"old\r\nkeep\r\n", b"keep\nnew\n"),
        )
