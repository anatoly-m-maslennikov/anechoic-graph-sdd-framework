"""Select only complete native Model Declaration Claims."""

from pathlib import Path
import sys
import unittest


PROGRAMMATIC = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_FORMAL_MODEL_ENGINE.model_declaration_sources import select_model_claims


CLAIM = "from caprmedio.formal_claims import declare_entity\ndeclare_entity(entity_name='Atom')\n"


def carrier(subject="CAPRMEDIO_MODEL <+ Atom", *, identifier="CA-R-1", status="active", body=None):
    if body is None:
        body = f"## Claim\n\n### Formal Claim\n\n```python\n{CLAIM}```\n"
    return {
        "source": {"path": f"{identifier}.md", "atom_id": identifier},
        "read_view": {"status": status, "content_role": "Requirement"},
        "subjects": {"governs": subject},
        "body": body,
    }


class ModelDeclarationSourceTests(unittest.TestCase):
    def test_selects_model_and_ignores_structure_and_draft(self):
        model = carrier()
        structure = carrier("CAPRMEDIO_STRUCTURE <+ Scope Unit//ENGINE", identifier="CA-R-2", body="")
        draft = carrier(identifier="CA-R-3", status="draft", body="")
        self.assertEqual(select_model_claims([structure, draft, model]), (CLAIM,))

    def test_duplicate_subject_and_identifier_fail_with_source(self):
        with self.assertRaisesRegex(ValueError, "CA-R-2.md: duplicate Declaration Subject"):
            select_model_claims([carrier(), carrier(identifier="CA-R-2")])
        with self.assertRaisesRegex(ValueError, "CA-R-1.md: duplicate Current Declaration ID"):
            select_model_claims([carrier(), carrier("CAPRMEDIO_MODEL <+ Node")])

    def test_mixed_missing_unclosed_and_non_native_claims_fail(self):
        formal = "## Claim\n### Formal Claim\n"
        bodies = (
            formal,
            formal + f"```python\n{CLAIM}```\n```CFEL\nNode\n```\n",
            formal + f"```python\n{CLAIM}",
            formal + "```python\nproperty_rule(address='Atom.Name')\n```\n",
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, "CA-R-1.md:"):
                select_model_claims([carrier(body=body)])

    def test_prose_example_is_not_a_formal_claim(self):
        body = f"## Claim\n### Prose Claim\n```python\n{CLAIM}```\n"
        with self.assertRaisesRegex(ValueError, "expected one Formal Claim"):
            select_model_claims([carrier(body=body)])

    def test_unparseable_subject_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "invalid Main Subject"):
            select_model_claims([carrier("CAPRMEDIO_MODEL <+")])

    def test_empty_model_is_an_error(self):
        structure = carrier("CAPRMEDIO_STRUCTURE <+ Scope Unit//ENGINE", body="")
        with self.assertRaisesRegex(ValueError, "No Current CAPRMEDIO_MODEL Declarations"):
            select_model_claims([structure])


if __name__ == "__main__":
    unittest.main()
