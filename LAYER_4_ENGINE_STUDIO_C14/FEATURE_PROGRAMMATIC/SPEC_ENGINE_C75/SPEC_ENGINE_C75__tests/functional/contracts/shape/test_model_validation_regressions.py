import sys
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
        parse_cli_contract,
        parse_trace_contract,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import parse_shape  # fmt: skip


class ModelValidationRegressions(unittest.TestCase):
    def test_order_endpoint_details_keep_json_types(self):
        for parser, prefix in (
            (
                parse_trace_contract,
                "declare_trace_contract(action='a', output='o', ",
            ),
            (
                parse_cli_contract,
                "declare_cli_contract(interface='i', action='a', runner='r', "
                "path='p', output='o', ",
            ),
        ):
            for required, endpoint in (
                ("1", "True"),
                ("True", "1"),
                ("0", "False"),
                ("False", "0"),
            ):
                source = (
                    prefix
                    + "must_effect=(('target', 'done', {'value': "
                    + required
                    + "}),), "
                    "must_precede=((('before', 'done'), ('target', 'done', "
                    "{'value': " + endpoint + "})),))"
                )
                with self.subTest(
                    parser=parser.__name__,
                    required=required,
                    endpoint=endpoint,
                ):
                    with self.assertRaisesRegex(
                        ValueError, "required second effect"
                    ):
                        parser(source)
                    self.assertTrue(
                        parser(
                            source.replace(
                                "'value': " + endpoint + "})),))",
                                "'value': " + required + "})),))",
                            )
                        )
                    )

    @unittest.skipUnless(
        sys.version_info >= (3, 12),
        "generic class syntax requires Python 3.12",
    )
    def test_shape_rejects_type_parameters_on_either_class(self):
        for record, subtype in (("Atom[T]", "Plan"), ("Atom", "Plan[T]")):
            source = (
                f"class {record}:\n    header: Header\n\nclass {subtype}"
                "(Atom):\n    pass\n"
            )
            with (
                self.subTest(source=source),
                self.assertRaisesRegex(
                    ValueError, "unsupported shape class syntax"
                ),
            ):
                parse_shape(source, "solution")
        self.assertEqual(
            "Atom",
            parse_shape(
                "class Atom:\n    header: Header\n\nclass Plan(Atom):\n    "
                "pass\n",
                "solution",
            )["record"],
        )
