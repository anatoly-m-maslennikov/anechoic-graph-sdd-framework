"""The native Header writer preserves authored data in canonical order."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header, native_header_model_fields, native_header_view


class NativeCarrierHeaderTests(unittest.TestCase):
    def setUp(self):
        self.old = {
            "identity": {"atom_id": "AN-T-1"},
            "context": {"template": "task", "tier": 3, "container": {"component": "C00"}},
            "state": {"updated_at": "2026-11-20T00:00:00+00:00", "version": 1, "status": "active"},
        }

    def test_round_trip_preserves_authored_fields_in_order(self):
        original = self.old | {
            "concern": {"components": ["C21"]},
            "relations": {"REFERENCES": ["AN-S-1@1"]},
        }
        header = canonical_native_header(original)
        self.assertEqual(tuple(header), ("atom_family", "atom_id", "concern", "container", "priority", "context", "relations", "state"))
        self.assertEqual(header["concern"], [{"subject": "C21", "path": "Project Structure.components", "relation": "affects"}])
        self.assertEqual(tuple(header["state"]), ("status", "version", "updated_at"))
        self.assertEqual((header["container"], header["priority"]), ({"component": "C00"}, 2))
        self.assertEqual(header["context"], {"template": "task"})
        self.assertEqual(header["relations"], original["relations"])
        self.assertEqual(native_header_view(header)["identity"], original["identity"])
        self.assertEqual(canonical_native_header(header), header)
        self.assertIn("tier", self.old["context"])

    def test_family_rules_and_untransferred_package_id(self):
        header = canonical_native_header(self.old)
        for invalid in (
            header | {"atom_family": "SPEC"},
            header | {"tier": 1},
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
        self.assertEqual((canonical_native_header(package)["container"], canonical_native_header(package)["tier"]), ({"component": "C9"}, 0))

    def test_issue_concern_round_trips_affected_components(self):
        issue = self.old | {"context": self.old["context"] | {"template": "problem"}}
        concern = {"components": ["C21", "C45"]}
        header = canonical_native_header(issue | {"concern": concern})
        locators = [{"subject": value, "path": "Project Structure.components", "relation": "affects"} for value in concern["components"]]
        self.assertEqual(header["concern"], locators)
        self.assertEqual(native_header_view(header)["concern"], locators)
        self.assertEqual(canonical_native_header(header), header)
        self.assertEqual(native_header_model_fields(header)["concern"], locators)
        self.assertNotIn("components", native_header_model_fields(header))
        for invalid in ([], "C21", ["C21", "C21"], ["MCP"], [21]):
            with self.subTest(components=invalid), self.assertRaises(ValueError):
                canonical_native_header(issue | {"concern": {"components": invalid}})
        with self.assertRaises(ValueError):
            canonical_native_header(issue | {"concern": {"subject": "Atom", "path": "Model", "relation": "about"}})
        with self.assertRaises(ValueError):
            native_header_view(header | {"concern": ["component(id=C21);exec(x)"]})

    def test_ticket_concern_validation_and_historical_references(self):
        first = {"subject": "C51", "path": "Project Structure.components", "relation": "affects"}
        second = {"subject": "AN-S-1", "path": "Model", "relation": "about"}
        header = canonical_native_header(self.old | {"concern": [first, second]})
        self.assertEqual(native_header_view(header)["concern"], [first, second])
        for invalid in ([], [first, first], [{"subject": "C51"}], [first | {"extra": "x"}],
                        [first | {"path": " "}]):
            with self.subTest(concern=invalid), self.assertRaises(ValueError):
                native_header_view(header | {"concern": invalid})
        historical = header | {"concern": ["component(id=C51)", "atom(id=AN-S-1)"]}
        self.assertEqual(native_header_view(historical)["concern"], historical["concern"])
        with self.assertRaisesRegex(ValueError, "cannot be converted"):
            canonical_native_header(historical)
        self.assertEqual(canonical_native_header(header | {"concern": ["component(id=C51)"]})["concern"], [first])
        grouped = {key: value for key, value in header.items() if key not in {"container", "priority"}}
        grouped |= {"structure": {"container": header["container"], "priority": header["priority"]},
                    "concern": {"components": ["C51"]}}
        self.assertEqual(native_header_view(grouped)["concern"], {"components": ["C51"]})
        self.assertEqual(canonical_native_header(grouped)["concern"], [first])

    def test_legacy_nested_read_and_missing_spec_tier(self):
        nested = {"atom_family": "SPEC", "atom_id": "AN-S-1", "structure": {"container": {"component": "C9"}},
                  "context": {"lens": "SPEC"}, "state": self.old["state"]}
        self.assertEqual(native_header_view(nested)["context"]["container"], {"component": "C9"})
        with self.assertRaisesRegex(ValueError, "Tier"):
            canonical_native_header(nested)
        flat = {key: value for key, value in nested.items() if key != "structure"} | nested["structure"]
        with self.assertRaisesRegex(ValueError, "Tier"):
            native_header_view(flat)
        self.assertEqual(native_header_model_fields(flat | {"tier": 2})["tier"], 2)

    def test_component_concern_is_ticket_only(self):
        locator = {"subject": "Atom", "path": "Model", "relation": "about"}
        for atom_id, context in (("AN-S-1", {"container": {"component": "C9"}, "tier": 1}),
                                 ("AN-P-1", {"container": {"component": "C9"}, "template": "manifest"})):
            source = self.old | {"identity": {"atom_id": atom_id}, "context": context}
            header = canonical_native_header(source | {"concern": locator})
            self.assertEqual(native_header_view(header)["concern"], locator)
            for concern in ({"components": ["C9"]}, locator | {"components": ["C9"]}):
                with self.subTest(atom_id=atom_id, concern=concern):
                    with self.assertRaisesRegex(ValueError, "Concern"):
                        native_header_view(header | {"concern": concern})
                    with self.assertRaisesRegex(ValueError, "Concern"):
                        canonical_native_header(source | {"concern": concern})
            with self.assertRaisesRegex(ValueError, "Concern"):
                canonical_native_header(source | {"concern": locator | {"unknown": "value"}})
            archived = header | {"concern": {"components": ["C9"]},
                                 "state": header["state"] | {"status": "archived"}}
            self.assertEqual(native_header_view(archived)["concern"], {"components": ["C9"]})
            with self.assertRaisesRegex(ValueError, "Concern"):
                canonical_native_header(archived)

    def test_project_config_and_legacy_pmeta_headers(self):
        source = self.old | {"identity": {"atom_id": "AN-P-1"},
                             "context": {"container": {"component": "C00"}},
                             "state": self.old["state"] | {"status": "draft"}}
        canonical = canonical_native_header(source)
        self.assertEqual(canonical["atom_family"], "PROJECT_CONFIG")
        current = canonical_native_header(source | {"identity": {"atom_id": "AN-C-3193"},
            "context": {"container": {"component": "C00"}, "template": "model_manifest"},
            "state": self.old["state"]})
        self.assertEqual(current["atom_family"], "PROJECT_CONFIG")
        self.assertEqual(native_header_view(current)["identity"]["atom_id"], "AN-C-3193")
        self.assertEqual(canonical_native_header(current), current)
        legacy = canonical | {"atom_family": "PMETA"}
        self.assertEqual(native_header_view(legacy)["atom_family"], "PROJECT_CONFIG")
        self.assertEqual(native_header_model_fields(legacy)["atom_family"], "PROJECT_CONFIG")
        self.assertEqual(canonical_native_header(legacy), canonical)
        self.assertEqual(canonical["atom_id"], "AN-P-1")

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
