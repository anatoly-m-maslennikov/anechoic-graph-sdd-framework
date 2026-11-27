"""Static analysis for source comments and regression tests for the purge."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    source_comments as lint,
)

NEXT_LINE_DIRECTIVE = "editorconfig-checker-disable-next-line"


class SourceCommentsTests(unittest.TestCase):
    def test_source_has_no_ordinary_comments(self):
        findings = lint.check_sources(lint.ROOT)
        if findings:
            self.fail(
                "\n".join(
                    [
                        *findings,
                        "Run source_comments.py --fix to remove "
                        + "these comments.",
                    ]
                )
            )

    def test_python_purge_keeps_strings_and_directives(self):
        source = (
            "#!/usr/bin/env python3\r\n# coding: utf-8\r\n"
            "# prose\r\nvalue = 'literal # text'  # inline prose\r\n"
            "# editorconfig-checker-disable-line\r\n"
            f"# {NEXT_LINE_DIRECTIVE}\r\n"
            "from other import value  # noqa: F401\r\n"
        )
        edits = lint.remove_line_comments(source, lint.python_comments(source))
        for start, end, replacement in reversed(edits):
            source = source[:start] + replacement + source[end:]
        self.assertEqual(
            "#!/usr/bin/env python3\r\n# coding: utf-8\r\n"
            "value = 'literal # text'\r\n"
            "# editorconfig-checker-disable-line\r\n"
            "from other import value  # noqa: F401\r\n",
            source,
        )

    def test_docker_purge_keeps_editorconfig_directives(self):
        source = (
            "# editorconfig-checker-disable-line\n"
            f"# {NEXT_LINE_DIRECTIVE}\n"
            "# ordinary comment\n"
            "FROM python:3.12\n"
        )
        removed = lint.docker_comments(lint.Path("Dockerfile"), source)
        self.assertEqual(
            [f"# {NEXT_LINE_DIRECTIVE}", "# ordinary comment"],
            [source[start:end] for start, end in removed],
        )

    def web_fixture(self):
        source = (
            "<script>\n// @ts-nocheck\n"
            "// editorconfig-checker-disable-line\n"
            f"// {NEXT_LINE_DIRECTIVE}\n"
            'let url = "🙂 https://example.org"; // prose\n'
            "let slash = /https?:\\/\\//;\n</script>\n"
            "<p>{url}<!-- editorconfig-checker-disable-line -->{slash}</p>\n"
            f"<style>/* {NEXT_LINE_DIRECTIVE} */\n"
            "/* prose */ p { color: red; }</style>\n"
        )
        edits, css_edits, ts_edits = lint.web_edits(
            lint.ROOT,
            [
                {"path": "Fixture.svelte", "source": source},
                {
                    "path": "fixture.css",
                    "source": "a { color: red/* separate */blue; }",
                },
                {
                    "path": "fixture.ts",
                    "source": "// editorconfig-checker-disable-line\n"
                    "const value = 1; // prose\n",
                },
            ],
        )
        return source, edits, css_edits, ts_edits

    def test_web_purge_keeps_syntax_and_directives(self):
        source, edits, css_edits, ts_edits = self.web_fixture()
        self.assertEqual([(14, 28, None)], css_edits)
        self.assertEqual(4, len(edits))
        self.assertEqual(1, len(ts_edits))
        for start, end, replacement in sorted(edits, reverse=True):
            source = source[:start] + replacement + source[end:]
        ts_source = (
            "// editorconfig-checker-disable-line\nconst value = 1; // prose\n"
        )
        for start, end, replacement in reversed(ts_edits):
            ts_source = ts_source[:start] + replacement + ts_source[end:]
        self.assertNotIn("prose", source)
        self.assertIn("// @ts-nocheck", source)
        self.assertIn("// editorconfig-checker-disable-line", source)
        self.assertNotIn(NEXT_LINE_DIRECTIVE, source)
        self.assertIn("<!-- editorconfig-checker-disable-line -->", source)
        self.assertIn('"🙂 https://example.org"', source)
        self.assertIn("/https?:\\/\\//", source)
        self.assertIn(
            "<p>{url}<!-- editorconfig-checker-disable-line -->{slash}</p>",
            source,
        )
        self.assertIn("// editorconfig-checker-disable-line", ts_source)
        self.assertNotIn("prose", ts_source)
