import re
import unittest
from pathlib import Path
from unittest.mock import patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier import (
    carrier_runtime_effects as MOD,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = (
    ROOT
    / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/carriers/content/carrier_body__pub.py"
)


class CarrierEffectsTest(unittest.TestCase):
    def setUp(self):
        self.fixed = SOURCE.read_text()
        self.old = self.fixed.replace(
            '_CLOSING_DELIMITER = re.compile(rb"\\r?\\n---\\r?\\n")\n\n\n', ""
        ).replace(
            "_CLOSING_DELIMITER.search(raw, pos=opening_end - 1)",
            're.search(rb"\\r?\\n---\\r?\\n", raw, opening_end - 1)',
        )

    def test_resolved_bindings_and_transitive_effects(self):
        fixed = MOD.analyze_carrier(self.fixed)
        old = MOD.analyze_carrier(self.old)
        self.assertEqual(
            (fixed["status"], old["status"]), ("permitted", "permitted")
        )
        self.assertEqual((fixed["variant"], old["variant"]), ("fixed", "old"))
        self.assertEqual(fixed["import_call"]["callable"], "re.compile")
        f = fixed["functions"]["frontmatter_bounds"]
        self.assertTrue(
            any(
                c["callable"] == "re.Pattern.search" and "pos" in c["binding"]
                for c in f["calls"]
            )
        )
        self.assertTrue(
            any(
                c["callable"] == "re.search" and "flags" in c["binding"]
                for c in old["functions"]["frontmatter_bounds"]["calls"]
            )
        )
        caller = old["functions"]["source_body"]
        self.assertTrue(
            any(
                c["callable"] == "carrier_body.frontmatter_bounds"
                for c in caller["calls"]
            )
        )
        self.assertIn("private_regex_cache", caller["transitive_effects"])
        self.assertIn("private_regex_cache", fixed["import_call"]["effects"])
        self.assertIn("module initialization", fixed["import_review"])
        self.assertEqual(re.search(b"a", b"ba", 1).span(), (1, 2))
        self.assertIsNone(re.compile(b"a").search(b"ba", pos=2))

    def test_forbidden_and_unresolved_cannot_pass(self):
        self.assertEqual(MOD.check_effects(["local"]), "permitted")
        self.assertEqual(MOD.check_effects(["local", "io"]), "forbidden")
        self.assertEqual(MOD.check_effects(["local", "mystery"]), "unresolved")
        self.assertEqual(MOD.check_effects([]), "unresolved")
        target = "return raw[bounds[2] :]"
        self.assertEqual(self.fixed.count(target), 1)
        self.assertEqual(
            MOD.analyze_carrier(
                self.fixed.replace(target, "return unknown(raw)")
            )["status"],
            "unresolved",
        )
        with patch.object(
            MOD.platform, "python_version", return_value="3.14.8"
        ):
            self.assertEqual(
                MOD.analyze_carrier(self.fixed)["status"], "unresolved"
            )


if __name__ == "__main__":
    unittest.main()
