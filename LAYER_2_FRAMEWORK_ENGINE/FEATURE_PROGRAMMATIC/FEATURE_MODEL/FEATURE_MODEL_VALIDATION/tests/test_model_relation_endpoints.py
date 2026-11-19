"""Check native Relation endpoint levels and inverse direction."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_endpoints import validate_relation_endpoint_levels


def relation(arguments):
    return parse_native_model_claim(
        "from anechoic.formal_claims import declare_relation\n"
        f"declare_relation(relation_name='R', inverse_alias='REVERSE', {arguments})\n"
    )


class RelationEndpointTests(unittest.TestCase):
    def test_both_levels_default_independently(self):
        claim = relation("source_endpoint={}, target_endpoint={'level': 'instances'}")
        for source in ("model_entities", "instances"):
            validate_relation_endpoint_levels(claim, "R", source, "instances")
            with self.assertRaisesRegex(ValueError, "not admitted"):
                validate_relation_endpoint_levels(claim, "R", source, "model_entities")

    def test_paired_domains_and_inverse_swap(self):
        claim = relation(
            "endpoint_pairs=("
            "{'source_endpoint': {'level': 'model_entities'}, 'target_endpoint': {'level': 'model_entities'}},"
            "{'source_endpoint': {'level': 'instances'}, 'target_endpoint': {'level': 'instances'}},)"
        )
        for level in ("model_entities", "instances"):
            validate_relation_endpoint_levels(claim, "R", level, level)
        with self.assertRaisesRegex(ValueError, "not admitted"):
            validate_relation_endpoint_levels(claim, "R", "instances", "model_entities")
        instance_of = relation("source_endpoint={'level': 'instances'}, "
                               "target_endpoint={'level': 'model_entities'}")
        validate_relation_endpoint_levels(instance_of, "R", "instances", "model_entities")
        validate_relation_endpoint_levels(instance_of, "REVERSE", "model_entities", "instances")
        with self.assertRaisesRegex(ValueError, "not admitted"):
            validate_relation_endpoint_levels(instance_of, "REVERSE", "instances", "model_entities")

    def test_invalid_names_levels_and_incomplete_declarations_fail(self):
        claim = relation("source_endpoint={}, target_endpoint={}")
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_relation_endpoint_levels(claim, "UNKNOWN", "instances", "instances")
        with self.assertRaisesRegex(ValueError, "Actual endpoint level"):
            validate_relation_endpoint_levels(claim, "R", "both", "instances")
        with self.assertRaisesRegex(ValueError, "Missing target_endpoint"):
            validate_relation_endpoint_levels(
                {"kind": "relation", "arguments": {"relation_name": "R", "source_endpoint": {}}},
                "R", "instances", "instances",
            )
