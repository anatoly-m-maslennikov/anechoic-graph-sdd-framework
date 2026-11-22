"""Workbench registry parity for allowed classification values."""

from pathlib import Path
import unittest

WORKBENCH = Path(__file__).resolve().parents[2]
PROGRAMMATIC = WORKBENCH.parents[1] / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.compiler_claim_fixtures__pub import (
    CLASSIFICATION_CFEL_BODY, CLASSIFICATION_PYTHON_BODY,
)
from KERNEL_MIXER_C59.relation_registry import compile_relation_registry


class AllowedClassificationValuesRegistryTests(unittest.TestCase):
    def test_allowed_values_match_across_claim_languages(self):
        def wb(body):
            return {'id':'CA-R-2484','ref':'CA-R-2484','version':2,'source_path':'R2484.md',
                    'status_group':'Current','role':'Requirement','form':'Rule',
                    '_content_bytes':body.encode(),'content_markdown':body}
        self.assertEqual(compile_relation_registry([wb(CLASSIFICATION_CFEL_BODY)]),
                         compile_relation_registry([wb(CLASSIFICATION_PYTHON_BODY)]))


if __name__ == '__main__':
    unittest.main()
