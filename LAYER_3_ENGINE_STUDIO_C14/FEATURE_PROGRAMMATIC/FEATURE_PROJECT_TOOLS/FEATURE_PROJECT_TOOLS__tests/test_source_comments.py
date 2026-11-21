"""Static analysis for source comments and regression tests for the purge."""

import unittest

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    source_comments as lint,
)


class SourceCommentsTests(unittest.TestCase):
    def test_source_has_no_ordinary_comments(self):
        findings = lint.check_sources(lint.ROOT)
        if findings:
            self.fail("\n".join([*findings, "Run source_comments.py --fix to remove these comments."]))

    def test_python_purge_keeps_strings_and_directives(self):
        source = (
            "#!/usr/bin/env python3\r\n# coding: utf-8\r\n"
            "# prose\r\nvalue = 'literal # text'  # inline prose\r\n"
            "from other import value  # noqa: F401\r\n"
        )
        edits = lint.remove_line_comments(source, lint.python_comments(source))
        for start, end, replacement in reversed(edits):
            source = source[:start] + replacement + source[end:]
        self.assertEqual(
            "#!/usr/bin/env python3\r\n# coding: utf-8\r\n"
            "value = 'literal # text'\r\nfrom other import value  # noqa: F401\r\n",
            source,
        )

    def test_web_purge_keeps_syntax_and_directives(self):
        source = (
            '<script>\n// @ts-nocheck\nlet url = "🙂 https://example.org"; // prose\n'
            'let slash = /https?:\\/\\//;\n</script>\n'
            '<p>{url}<!-- prose -->{slash}</p>\n<style>/* prose */ p { color: red; }</style>\n'
        )
        edits, css_edits = lint.web_edits(lint.ROOT, [
            {"path": "Fixture.svelte", "source": source},
            {"path": "fixture.css", "source": "a { color: red/* separate */blue; }"},
        ])
        self.assertEqual([(14, 28, None)], css_edits)
        self.assertEqual(3, len(edits))
        for start, end, replacement in sorted(edits, reverse=True):
            source = source[:start] + replacement + source[end:]
        self.assertNotIn("prose", source)
        self.assertIn("// @ts-nocheck", source)
        self.assertIn('"🙂 https://example.org"', source)
        self.assertIn('/https?:\\/\\//', source)
        self.assertIn("<p>{url}{slash}</p>", source)
