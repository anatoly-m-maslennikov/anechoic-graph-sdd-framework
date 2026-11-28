"""Check the Form declaration input to the Model compiler."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared \
    import FORM_EXAMPLES  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    NativeModelClaimError,
    parse_native_model_claim,
)


class NativeFormParityTests(unittest.TestCase):
    def test_form_roles_require_a_nonempty_role_list(self):
        source = FORM_EXAMPLES[0][1]
        roles = (
            "Requirement",
            "Method",
            "Evaluation",
            "Delivery",
            "Operations",
        )
        self.assertEqual(
            roles, parse_native_model_claim(source)["arguments"]["form_roles"]
        )
        invalid = source.replace(repr(roles), "()")
        with self.assertRaisesRegex(
            NativeModelClaimError,
            "form_roles requires one Form and distinct Roles",
        ):
            parse_native_model_claim(invalid)


if __name__ == "__main__":
    unittest.main()
