"""Check that C45 formal comparison reads the Manifest Contract."""

import unittest
from itertools import cycle
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import NonCallableMock, patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.\
    http.backend_http_formal import (
    _carrier,
    _facts,
)  # fmt: skip

_BASE = (
    "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/"
    "FEATURE_IWE_CONSOLE_BACKEND_C45/"
)
_SOLUTION = _BASE + (
    "AN-S-3371-DES-SOLUTION--run-one-validated-read-only-workbench-query.md"
)
_LEGACY_SOLUTION = _BASE + (
    "01_TIER_1_ARCHITECTURE/AN-S-3371-DES-DECISION--"
    "run-one-validated-read-only-workbench-query.md"
)
_LEGACY = """---
atom_family: SPEC
atom_id: AN-S-3371
container:
  component: C45
tier: 1
context:
  template: DECISION
relations:
  IS_SOLUTION_FOR:
  - AN-S-3185@11
state:
  status: active
  version: 5
---
"""


def _manifest_and_solution():
    manifest = NonCallableMock(
        spec_set=["body", "metadata"],
        body="manifest",
        metadata={
            "tier": 1,
            "context": {"template": "component_manifest"},
        },
    )
    solution = NonCallableMock(
        spec_set=["body", "metadata"],
        body="solution",
        metadata={"tier": 1},
    )
    return manifest, solution


class FormalHttpTests(unittest.TestCase):
    def test_solution_paths_and_schema(self):
        legacy = _LEGACY
        canonical = (
            legacy.replace("tier: 1", "tier: 0")
            .replace("template: DECISION", "template: solution")
            .replace("IS_SOLUTION_FOR:", "ANSWERS:")
            .replace("AN-S-3185@11", "AN-S-3059@58")
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            new = root / _SOLUTION
            old = root / _LEGACY_SOLUTION
            new.parent.mkdir(parents=True)
            old.parent.mkdir(parents=True)
            old.write_text(legacy)
            parsed, evidence = _carrier(root, "solution", "AN-S-3371", "C45")
            self.assertEqual(evidence["path"], _LEGACY_SOLUTION)
            self.assertIn(
                "AN-S-3185@11", parsed.metadata["relations"]["IS_SOLUTION_FOR"]
            )
            old.unlink()
            new.write_text(canonical)
            parsed, evidence = _carrier(root, "solution", "AN-S-3371", "C45")
            self.assertEqual(evidence["path"], _SOLUTION)
            self.assertEqual(
                parsed.metadata["relations"]["ANSWERS"], ["AN-S-3059@58"]
            )
            old.write_text(legacy)
            with self.assertRaisesRegex(ValueError, "exactly one active"):
                _carrier(root, "solution", "AN-S-3371", "C45")
            old.unlink()
            new.write_text(
                canonical.replace("template: solution", "template: decision")
            )
            with self.assertRaisesRegex(ValueError, "tier or template"):
                _carrier(root, "solution", "AN-S-3371", "C45")

    def test_manifest_contract_keeps_source_provenance(self):
        manifest, solution = _manifest_and_solution()
        evidence = {"atom_id": "AN-S-3059", "version": 58, "sha256": "digest"}
        fields = {
            "component_id": "C45",
            "boundaries": {"io": {"server": {"tool_api": {}}}},
        }
        module = (
            "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.http.backend"
            "_http_formal."
        )
        for key in ("operation", "endpoint"):
            claim = {key: "POST /tools", "facts": {}, "outcomes": []}
            with (
                self.subTest(key=key),
                patch(
                    module + "_carrier",
                    side_effect=cycle(
                        [
                            (manifest, evidence),
                            (solution, {"atom_id": "AN-S-3371"}),
                        ]
                    ),
                ),
                patch(
                    module + "parse_component_manifest",
                    return_value=(fields, None),
                ),
                patch(
                    module + "component_contract_fences",
                    return_value=[("python contract", "claim")],
                ),
                patch(module + "parse_contract", return_value=claim),
                patch(module + "manifest_tool_api", return_value=({}, {})),
            ):
                _, expected, *_, sources = _facts(None)
                self.assertEqual(expected["operation"], ["POST /tools"])
                self.assertEqual(sources["contract"], evidence)
                self.assertEqual(sources["manifest"], evidence)
                self.assert_solution_pin(solution)

    def assert_solution_pin(self, solution):
        solution.metadata = {
            "tier": 0,
            "relations": {"ANSWERS": ["AN-S-3059@58"]},
        }
        _facts(None)
        solution.metadata["relations"]["ANSWERS"] = ["AN-S-3059@57"]
        with self.assertRaisesRegex(ValueError, "exact ANSWERS"):
            _facts(None)
        solution.metadata = {"tier": 1}
