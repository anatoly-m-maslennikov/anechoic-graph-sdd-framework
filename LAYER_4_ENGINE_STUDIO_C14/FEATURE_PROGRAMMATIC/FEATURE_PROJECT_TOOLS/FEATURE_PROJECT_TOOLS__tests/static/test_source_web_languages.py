"""Check the executable source language rule."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    static_checks,
)


lint = static_checks.source_languages.source_web_languages


class SourceWebLanguageTests(unittest.TestCase):
    def test_javascript_modules_report_their_path(self):
        for name in ("ui.jsx", "build.mjs", "analyze.cjs", "smoke.js"):
            with self.subTest(name=name):
                self.assertEqual(
                    [
                        f"{name}: authored JavaScript source must use TypeScript"
                    ],
                    lint.web_language_findings(Path("."), Path(name)),
                )

    def test_typed_source_and_fixture_data_are_outside_the_file_rule(self):
        for name in (
            "app.ts",
            "view.tsx",
            "view.svelte",
            "before.mjs.txt",
            "package.json",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    [], lint.web_language_findings(Path("."), Path(name))
                )

    def test_html_reports_only_inline_executable_script_blocks(self):
        source = "\n".join(
            (
                "<!-- <script>comment()</script> -->",
                "<textarea><script>text()</script></textarea>",
                "<noscript><script>disabled()</script></noscript>",
                '<script type="application/json">{"script": "text"}</script>',
                '<script type="importmap">{"imports": {}}</script>',
                '<script type="module" src="/src/main.ts"></script>',
                "<script> </script>",
                '<script>run("<script>")</script>',
                '<script type="module">runModule()</script>',
                '<script type="TEXT/JAVASCRIPT">runClassic()</script>',
                '<script language="javascript1.5">runLegacy()</script>',
            )
        )
        with TemporaryDirectory() as directory:
            root, path = Path(directory), Path("index.html")
            (root / path).write_text(source, encoding="utf-8")
            self.assertEqual(
                [
                    f"index.html:{line}: inline JavaScript must be built from TypeScript source"
                    for line in (8, 9, 10, 11)
                ],
                lint.web_language_findings(root, path),
            )

    def test_svelte_checks_instance_and_module_scripts_with_its_parser(self):
        source = (
            "<script module>let moduleValue = 1;</script>\n"
            '<script lang="ts">let value: number = 1;</script>\n'
            '<p>{"<script>literal()</script>"}{value}</p>\n'
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Mixed.svelte").write_text(source, encoding="utf-8")
            (root / "Instance.svelte").write_text(
                "\n<script>let value = 1;</script>", encoding="utf-8"
            )
            (root / "Empty.svelte").write_text(
                "<script> </script>", encoding="utf-8"
            )
            self.assertEqual(
                [
                    'Mixed.svelte:1: Svelte script must use lang="ts"',
                    'Instance.svelte:2: Svelte script must use lang="ts"',
                ],
                lint.svelte_language_findings(
                    root,
                    [
                        Path("Mixed.svelte"),
                        Path("Instance.svelte"),
                        Path("Empty.svelte"),
                    ],
                ),
            )
