from pathlib import Path
import unittest

FEATURE = Path(__file__).resolve().parents[1]
PROGRAMMATIC = FEATURE.parent

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import FORM_EXAMPLES
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim  # noqa: E402




class NativeFormParityTests(unittest.TestCase):
    def test_role_and_content_consumers_match(self):
        with self.assertRaises(ValueError):
            parse_native_model_claim(FORM_EXAMPLES[0][1].replace("('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations')", "()"))



if __name__ == '__main__':
    unittest.main()
