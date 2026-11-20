"""The native Header writer preserves authored data in canonical order."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_carrier_header import canonical_native_header, native_header_model_fields, native_header_view


class NativeCarrierHeaderTests(unittest.TestCase):
    def setUp(self):
        self.old = {
            "identity": {"atom_id": "AN-T-1"},
            "context": {"template": "task", "tier": 3, "container": {"component": "C00"}},
            "state": {"updated_at": "2026-11-20T00:00:00+00:00", "version": 1, "status": "active"},
        }

    def test_round_trip_preserves_authored_fields_in_order(self):
        original = self.old | {
            "concern": {"path": "Model", "relation": "about", "subject": "Atom"},
            "relations": {"REFERENCES": ["AN-S-1@1"]},
        }
        header = canonical_native_header(original)
        self.assertEqual(tuple(header), ("atom_family", "atom_id", "concern", "structure", "context", "relations", "state"))
        self.assertEqual(tuple(header["concern"]), ("subject", "path", "relation"))
        self.assertEqual(tuple(header["state"]), ("status", "version", "updated_at"))
        self.assertEqual(header["structure"], {"container": {"component": "C00"}, "priority": 2})
        self.assertEqual(header["context"], {"template": "task"})
        self.assertEqual(header["relations"], original["relations"])
        self.assertEqual(native_header_view(header)["identity"], original["identity"])
        self.assertEqual(canonical_native_header(header), header)
        self.assertIn("tier", self.old["context"])

    def test_family_rules_and_untransferred_package_id(self):
        header = canonical_native_header(self.old)
        for invalid in (
            header | {"atom_family": "SPEC"},
            header | {"structure": header["structure"] | {"tier": 1}},
            header | {"context": {"template": "task", "lens": "QA"}},
            header | {"concern": {"subject": "Atom"}},
        ):
            with self.assertRaises(ValueError):
                native_header_view(invalid)
        package = {"identity": {"atom_id": "AN-S-1"},
                   "context": {"container": {"component": "C9"}, "template": "PKG", "lens": "SPEC", "package_id": "pkg1"},
                   "state": self.old["state"]}
        with self.assertRaisesRegex(ValueError, "Formal Claim"):
            canonical_native_header(package)
        del package["context"]["package_id"]
        package["context"]["tier"] = 0
        self.assertEqual(canonical_native_header(package)["structure"], {"container": {"component": "C9"}, "tier": 0})

    def test_issue_concern_round_trips_affected_components(self):
        issue = self.old | {"context": self.old["context"] | {"template": "problem"}}
        for locator in ({}, {"subject": "Atom", "path": "Model", "relation": "about"}):
            concern = locator | {"components": ["C21", "C45"]}
            header = canonical_native_header(issue | {"concern": concern})
            self.assertEqual(native_header_view(header)["concern"], concern)
            self.assertEqual(canonical_native_header(header), header)
            self.assertEqual(native_header_model_fields(header)["components"], ["C21", "C45"])
        for invalid in ([], "C21", ["C21", "C21"], ["MCP"], [21]):
            with self.subTest(components=invalid), self.assertRaisesRegex(ValueError, "Component IDs"):
                canonical_native_header(issue | {"concern": {"components": invalid}})

    def test_optional_ticket_label_is_separate_from_template(self):
        header = canonical_native_header(self.old | {"context": self.old["context"] | {"label": "Subtask"}})
        self.assertEqual(tuple(header["context"]), ("template", "label"))
        self.assertEqual(native_header_model_fields(header)["label"], "Subtask")
        self.assertEqual(native_header_model_fields(header)["template"], "task")
        with self.assertRaisesRegex(ValueError, "Label"):
            canonical_native_header(self.old | {
                "identity": {"atom_id": "AN-P-1"}, "context": header["context"] | {"container": {"component": "C00"}},
            })


if __name__ == "__main__":
    unittest.main()
