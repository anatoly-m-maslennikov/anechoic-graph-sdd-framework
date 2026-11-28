"""Check that classification values stay out of the Relation registry."""

from pathlib import Path
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared \
    import CLASSIFICATION_PYTHON_BODY  # fmt: skip
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_relation_registry


WORKBENCH = Path(__file__).resolve().parents[4]
PROGRAMMATIC = WORKBENCH.parents[1] / "FEATURE_PROGRAMMATIC"


class AllowedClassificationValuesRegistryTests(unittest.TestCase):
    def test_allowed_classification_values_do_not_declare_relations(self):
        body = CLASSIFICATION_PYTHON_BODY
        row = {
            "id": "CA-R-2484",
            "ref": "CA-R-2484",
            "version": 2,
            "source_path": "R2484.md",
            "status_group": "Current",
            "role": "Requirement",
            "form": "Rule",
            "_content_bytes": body.encode(),
            "content_markdown": body,
        }
        self.assertEqual(
            compile_relation_registry([row]), compile_relation_registry([])
        )


if __name__ == "__main__":
    unittest.main()
