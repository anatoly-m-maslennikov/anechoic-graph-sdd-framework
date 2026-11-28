from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


class TypedReferenceIntegration(unittest.TestCase):
    def test_native_classification_is_preserved(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
            parse_native_model_claim,
        )

        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.claims__shared import (
            _native_constraints,
        )

        claim = (
            "from anechoic.formal_claims import declare_entity\nclass "
            'Model:\n pass\ndeclare_entity(entity_class="Model",entity_name="M'
            'ODEL",axes={"Container":"yes"})'
        )
        rows = _native_constraints(
            parse_native_model_claim(claim),
            {"atom_id": "test", "version": 1},
            claim,
        )
        self.assertTrue(
            any(
                row["kind"] == "axis_condition"
                and row["axis"] == "Container"
                and row["value"] == "yes"
                for row in rows
            )
        )
