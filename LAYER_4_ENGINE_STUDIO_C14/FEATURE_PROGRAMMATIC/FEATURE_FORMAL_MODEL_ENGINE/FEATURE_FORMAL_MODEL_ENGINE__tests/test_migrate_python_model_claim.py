"""Checks for conservative CFEL migration and Markdown boundaries."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_python_model_claim


_TOOL = Path(__file__).resolve().parents[1] / "migrate_python_model_claim.py"
_LEXEMES = re.compile(
    r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|[A-Za-z_$][A-Za-z_0-9$]*|"
    r"\d+|::|\.\.|;>|:=|==|\(\(|\)\)|[^\s]"
)


def convert_carrier(raw, path):
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "atom.md"
        source.write_bytes(raw)
        frontier = {"records": [{"reference": "AN-S-1", "status_group": "Current",
                    "source_path_check": {"candidate": "atom.md"},
                    "candidates": [{"path": "atom.md", "contains_cfel": True,
                                    "sha256": hashlib.sha256(raw).hexdigest()}]}]}
        (root / "frontier.json").write_text(json.dumps(frontier))
        result = subprocess.run([sys.executable, "-B", str(_TOOL), "--audit", "frontier.json",
                                 "--stage", "stage"], cwd=root, capture_output=True, text=True, check=False)
        if result.returncode:
            raise AssertionError(result.stderr)
        output = root / "stage/atom.md"
        return output.read_bytes() if output.exists() else None


def convert_markdown_claim(body):
    header = b"---\natom_id: AN-S-1\n---\n"
    converted = convert_carrier(header + body.encode(), Path("atom.md"))
    return None if converted is None else converted[len(header):].decode()


def convert_claim(text):
    converted = convert_markdown_claim("## Claim\n### Formal Claim\n```CFEL\n" + text + "\n```\n")
    return None if converted is None else converted.split("```python\n", 1)[1].split("\n```", 1)[0]


def convert_statement(text):
    return convert_claim(text + ";")


class MigrationTests(unittest.TestCase):
    def test_supported_statements_round_trip(self):
        statements = (
            'Atom.Status :: [string]{::1}',
            'Atom.Status :: "A/B"',
            'Atom.Status :: [in (Draft, Active)]{::1}',
            'Atom.Header ;> Atom.Content',
            'Journal// {::0+}((CONTAINS)) Event Record//',
            'Atom.Status == Active',
            'Atom.Header.Context.Role :: "Analysis and Advisory"',
            'Project Structure <+ Aspects <+ Engineering',
            'Atom >> Carrier/File',
            'Atom.Header.State.Status >| (Status Order Number == 20)',
            'Atom/(.Header.State.Status >| Status Group = Current).Header.Path == PATH_TEMPLATE("<container>/<status folder>")',
            'Atom.Content.**[string]{::0+}',
            'Event Record.Relations.*[Relation//$relation]{::0+}',
            'Atom.Header.State.Version >= 1',
            'Scope Unit/Project//$scope_unit{::1}',
            'UNIQUE(Atom//$atom, (.Header.Identity.ID, .Header.State.Version))',
            'Atom/(.Header.Context.Role in (Operations))/Workflow',
        )
        for statement in statements:
            with self.subTest(statement=statement):
                result = convert_statement(statement)
                self.assertIsNotNone(result)
                self.assertEqual(_LEXEMES.findall(parse_python_model_claim(result)[0]), _LEXEMES.findall(statement))

    def test_unsupported_whole_claim_is_rejected(self):
        self.assertIsNone(convert_claim('Atom.Status :: [string]{::1};\nIF x THEN y;'))
        self.assertIsNone(convert_claim('Atom.Status :: [string]{::1}; # inline'))

    def test_form_role_constraint_round_trips(self):
        original = (
            'FOR EACH $a[<Atom>, (.Header.Context.Form = Decision)]:\n'
            '(\n    $a.Header.Context.Role:: [in (Method, Evaluation, Delivery, Operations)]{::1}\n)'
        )
        converted = convert_claim(original)
        self.assertIn('allow_roles_for_form(', converted)
        self.assertEqual(_LEXEMES.findall(original), _LEXEMES.findall(parse_python_model_claim(converted)[0]))

    def test_markdown_preserves_other_content_and_crlf(self):
        before = '## Claim\r\n### Formal Claim\r\n'
        after = '```\r\n### Prose Claim\r\nText.\r\n## Other\r\n```python\r\nkeep()\r\n```\r\n'
        body = before + '```CFEL\r\n# model\r\nAtom.Status :: [string]{::1};\r\n# instances\r\nAtom.Status == Active;\r\n' + after
        result = convert_markdown_claim(body)
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith(before + '```python\r\n# model\r\n'))
        self.assertIn('\r\n# instances\r\n', result)
        self.assertTrue(result.endswith(after))
        self.assertNotIn('\n', result.replace('\r\n', ''))

    def test_ambiguous_and_non_claim_fences_are_rejected(self):
        fence = '```CFEL\nAtom.Status :: [string]{::1};\n```\n'
        self.assertIsNone(convert_markdown_claim('## Claim\n### Formal Claim\n' + fence + fence))
        self.assertIsNone(convert_markdown_claim('## Other\n' + fence))
        self.assertIsNone(convert_markdown_claim('## Claim\n### Formal Claim\n```CFEL\nIF x THEN y;\n```\n'))

    def test_carrier_preserves_exact_header(self):
        header = b'---\r\nnote: "keep my quotes"\r\n---\r\n'
        body = b'## Claim\r\n### Formal Claim\r\n```CFEL\r\nAtom.Status :: [string]{::1};\r\n```\r\n'
        converted = convert_carrier(header + body, Path('atom.md'))
        self.assertIsNotNone(converted)
        self.assertTrue(converted.startswith(header))
        self.assertIn(b'```python\r\n', converted)


if __name__ == '__main__':
    unittest.main()
