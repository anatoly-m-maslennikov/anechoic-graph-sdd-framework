"""Native claim validation rejects invalid names and relation endpoints."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        NativeModelClaimError,
        parse_native_model_claim,
    )  # fmt: skip


class NativeModelClaimValidationTests(unittest.TestCase):
    def test_unknown_names_and_duplicate_keyword_fail_with_line(self):
        source = (
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Name", value_format=Missing)\n'
        )
        with self.assertRaisesRegex(
            NativeModelClaimError, "line 2.*unbound symbol: Missing"
        ):
            parse_native_model_claim(source)
        source = (
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Name", entity_name="Name")\n'
        )
        with self.assertRaisesRegex(
            NativeModelClaimError, "duplicate argument"
        ):
            parse_native_model_claim(source)

    def test_invalid_cardinality_and_property_bearer_are_rejected(self):
        prefix = "from anechoic.formal_claims import declare_entity\n"
        invalid = (
            (
                'declare_entity(entity_name="Name", '
                'relation_name="IS_PROPERTY_OF")'
            ),
            (
                'declare_entity(entity_name="Name", '
                'relation_name="IS_PROPERTY_OF", base_path=" ")'
            ),
            'declare_entity(entity_name="Name", value_cardinality=-1)',
            'declare_entity(entity_name="Name", value_cardinality=True)',
            'declare_entity(entity_name="Name", value_cardinality="1")',
            'declare_entity(entity_name="Name", '
            'instance_relation_constraints={"CONTAINS": '
            '{"targets_per_source": -1}})',
            'declare_entity(entity_name="Name", '
            'instance_property_constraints={"Name": '
            '{"value_cardinality": {"minimum": 2, "maximum": 1}}})',
        )
        for claim in invalid:
            with (
                self.subTest(claim=claim),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(prefix + claim)

    def test_invalid_relation_endpoints_are_rejected(self):
        prefix = "from anechoic.formal_claims import declare_relation\n"
        valid = '{"level": "instances"}'
        invalid = (
            "None",
            '{"level": None}',
            '{"level": "unknown"}',
            '{"level": "instances", "extra": "unexpected"}',
            '{"level": "instances", "entity_paths": "Atom"}',
            '{"level": "instances", "entity_paths": ("",)}',
            '{"level": "instances", "axis": 1}',
            '{"level": "instances", "ephemeral": "false"}',
        )
        for endpoint in invalid:
            for side in ("source_endpoint", "target_endpoint"):
                other = (
                    "target_endpoint"
                    if side == "source_endpoint"
                    else "source_endpoint"
                )
                claim = (
                    f'declare_relation(relation_name="R", {side}={endpoint}, '
                    f"{other}={valid})"
                )
                with (
                    self.subTest(side=side, endpoint=endpoint),
                    self.assertRaises(NativeModelClaimError),
                ):
                    parse_native_model_claim(prefix + claim)

    def test_relation_endpoint_levels_default_independently(self):
        prefix = "from anechoic.formal_claims import declare_relation\n"
        claim = (
            "declare_relation(relation_name='R', "
            "source_endpoint={'entity_paths': ('Node',)}, "
            "target_endpoint={'level': 'instances'})"
        )
        args = parse_native_model_claim(prefix + claim)["arguments"]
        self.assertEqual(
            args["source_endpoint"],
            {
                "entity_paths": ("Node",),
                "level": "model_entities_or_instances",
            },
        )
        self.assertEqual(args["target_endpoint"]["level"], "instances")

        claim = (
            "declare_relation(relation_name='R', endpoint_pairs=("
            "{'source_endpoint': {}, "
            "'target_endpoint': {'level': 'model_entities'}},"
            "{'source_endpoint': {'level': 'instances'}, "
            "'target_endpoint': {}},))"
        )
        pairs = parse_native_model_claim(prefix + claim)["arguments"][
            "endpoint_pairs"
        ]
        self.assertEqual(
            pairs[0]["source_endpoint"]["level"], "model_entities_or_instances"
        )
        self.assertEqual(
            pairs[0]["target_endpoint"]["level"], "model_entities"
        )
        self.assertEqual(pairs[1]["source_endpoint"]["level"], "instances")
        self.assertEqual(
            pairs[1]["target_endpoint"]["level"], "model_entities_or_instances"
        )

        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(
                prefix
                + "declare_relation(relation_name='R', source_endpoint={})"
            )


if __name__ == "__main__":
    unittest.main()
