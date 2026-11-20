from types import SimpleNamespace
from unittest import TestCase

from ATOM_LIFECYCLE.atom_instance_validation import _content_values, validate_atom_instance
from ATOM_LIFECYCLE.common import InputError


class AtomInstanceTests(TestCase):
    def setUp(self):
        self.view = {
            "atom_id": "CA-R-1", "ref_id": "CA-R-1", "role": "Requirement", "form": "Requirement",
            "tier": 1, "container": {"scope_unit": "CA-SU-00"}, "topics": {"main_subject": "Atom"},
            "status": "Active", "version": 1, "updated_at": "2026-01-01T00:00:00+00:00",
            "destination": {"file": {"name": "atom.md", "path": "."}},
        }
        self.schema = SimpleNamespace(rules=())
        self.body = "## Summary\n\nExample\n"

    def test_validates_complete_header_and_preserves_optional_absence(self):
        validate_atom_instance(self.view, self.body, self.schema)
        for invalid in ({"label": None}, {"relations": {"SPECIALIZES": []}}, {"context": {"extra": True}}):
            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                validate_atom_instance(self.view | invalid, self.body, self.schema)
        with self.assertRaisesRegex(InputError, "destination"):
            validate_atom_instance({key: value for key, value in self.view.items() if key != "destination"},
                                   self.body, self.schema)

    def test_only_declared_headings_create_properties(self):
        def rule(*path):
            return SimpleNamespace(path=path, prohibited=False, applies=lambda _: True)

        self.schema.rules = (rule("claim"), rule("claim", "prose_claim"))
        body = self.body + "\n## Claim\n\n### Prose Claim\n\nText.\n\n#### value\n\nA presentation heading.\n"
        claim = _content_values(self.view, body, self.schema)["properties"]["claim"]
        self.assertEqual(set(claim["properties"]), {"prose_claim"})
        prose = claim["properties"]["prose_claim"]
        self.assertIn("#### value", prose["value"])
        self.assertEqual(prose["properties"], {})
