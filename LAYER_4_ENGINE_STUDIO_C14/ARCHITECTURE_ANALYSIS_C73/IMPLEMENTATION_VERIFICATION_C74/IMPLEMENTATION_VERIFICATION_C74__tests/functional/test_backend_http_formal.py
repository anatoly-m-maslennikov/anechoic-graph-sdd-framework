"""Check that C45 formal comparison reads the Manifest Contract."""

from unittest.mock import NonCallableMock
from pathlib import Path
import unittest
from unittest.mock import patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.\
    backend_http_formal \
    import (
        _carrier,
        _facts,
    )  # fmt: skip


class FormalHttpTests(unittest.TestCase):
    def test_existing_solution_retains_its_obsolete_contract_pin(self):
        solution, _ = _carrier(
            Path(__file__).resolve().parents[5], "solution", "AN-S-3371", "C45"
        )
        self.assertIn(
            "AN-S-3185@11", solution.metadata["relations"]["IS_SOLUTION_FOR"]
        )

    def test_manifest_contract_keeps_source_provenance(self):
        manifest = NonCallableMock(
            spec_set=["body", "metadata"],
            body="manifest",
            metadata={
                "tier": 1,
                "context": {"template": "component_manifest"},
            },
        )
        solution = NonCallableMock(spec_set=["body"], body="solution")
        evidence = {"atom_id": "AN-S-3059", "version": 58, "sha256": "digest"}
        fields = {
            "component_id": "C45",
            "boundaries": {"io": {"server": {"tool_api": {}}}},
        }
        module = (
            "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.backend"
            "_http_formal."
        )
        for key in ("operation", "endpoint"):
            claim = {key: "POST /tools", "facts": {}, "outcomes": []}
            with (
                self.subTest(key=key),
                patch(
                    module + "_carrier",
                    side_effect=[
                        (manifest, evidence),
                        (solution, {"atom_id": "AN-S-3371"}),
                    ],
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
