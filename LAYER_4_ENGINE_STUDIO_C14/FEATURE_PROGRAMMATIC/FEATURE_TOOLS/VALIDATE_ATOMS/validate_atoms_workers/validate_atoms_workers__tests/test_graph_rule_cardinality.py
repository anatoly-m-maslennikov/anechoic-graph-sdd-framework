"""Cardinality Graph Rule validation and extraction."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.VALIDATE_ATOMS.\
    validate_atoms_workers.validate_atoms_workers__shared import (
    validate_graph_rule_body,
    validated_graph_rule_payload,
)  # noqa: E402  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.VALIDATE_ATOMS.\
    validate_atoms_workers.validate_atoms_workers__tests.\
    graph_rule_body_test_support import (
    CARDINALITY,
    Recorder,
)  # noqa: E402  # fmt: skip


def _invalid_cardinality_fields():
    return (
        CARDINALITY.replace(
            '  node: "Entity/Node/Continuant/Selection//'
            'Dependent Entity Occurrences"\n',
            "",
        ),
        CARDINALITY.replace("  relation_type: IS_BORNE_BY\n", ""),
        CARDINALITY.replace("  direction: outgoing\n", ""),
        CARDINALITY.replace(
            '  node: "Entity/Node/Continuant/Selection//'
            'Dependent Entity Occurrences"',
            "  node: null",
        ),
        CARDINALITY.replace(
            "  relation_type: IS_BORNE_BY", '  relation_type: "   "'
        ),
        CARDINALITY.replace("  direction: outgoing", "  direction: sideways"),
        CARDINALITY.replace("  other_endpoint:\n    - Entity\n", ""),
        CARDINALITY.replace(
            "  other_endpoint:\n    - Entity", "  other_endpoint: Entity"
        ),
        CARDINALITY.replace("    - Entity", "    - Entity///Node"),
        CARDINALITY.replace(
            '  node: "Entity/Node/Continuant/Selection//'
            'Dependent Entity Occurrences"',
            '  node: "Entity///Node"',
        ),
        CARDINALITY.replace(
            "  direction: outgoing", "  direction: outgoing\n  extra: true"
        ),
        CARDINALITY.replace("  maximum: 1", "  maximum: 1\n  extra: true"),
        CARDINALITY.replace(
            "  other_endpoint:\n    - Entity",
            "  source: [Entity]\n  target: [Entity]",
        ),
        CARDINALITY.replace("  minimum: 1\n", ""),
        CARDINALITY.replace("  maximum: 1\n", ""),
    )


class GraphRuleCardinalityTests(unittest.TestCase):
    def validate(self, body: str) -> Recorder:
        check = Recorder()
        validate_graph_rule_body(body, check)  # type: ignore[arg-type]
        return check

    def test_cardinality_exact_unbounded_and_zero_bounds_pass(self) -> None:
        variants = (
            CARDINALITY,
            CARDINALITY.replace("maximum: 1", "maximum: null"),
            CARDINALITY.replace("minimum: 1", "minimum: 0").replace(
                "maximum: 1", "maximum: 0"
            ),
        )
        for body in variants:
            with self.subTest(body=body):
                check = self.validate(body)
                self.assertEqual(check.findings, [])
                self.assertEqual(check.gaps, [])

    def test_cardinality_bounds_require_exact_nonnegative_ordered_integers(
        self,
    ) -> None:
        invalid = (
            CARDINALITY.replace("minimum: 1", "minimum: true"),
            CARDINALITY.replace("minimum: 1", "minimum: 1.0"),
            CARDINALITY.replace("minimum: 1", 'minimum: "1"'),
            CARDINALITY.replace("minimum: 1", "minimum: -1"),
            CARDINALITY.replace("maximum: 1", "maximum: -1"),
            CARDINALITY.replace("maximum: 1", "maximum: 0"),
            CARDINALITY.replace("minimum: 1", "minimum: null"),
            CARDINALITY.replace("maximum: 1", "maximum: 1.0"),
            CARDINALITY.replace("maximum: 1", 'maximum: "1"'),
            CARDINALITY.replace("maximum: 1", "maximum: true"),
        )
        for body in invalid:
            with self.subTest(body=body):
                check = self.validate(body)
                self.assertTrue(check.findings)
                self.assertEqual(check.gaps, [])

    def test_cardinality_closed_required_fields_and_subject_types(
        self,
    ) -> None:
        invalid = _invalid_cardinality_fields()
        for body in invalid:
            with self.subTest(body=body):
                check = self.validate(body)
                self.assertTrue(check.findings)
                self.assertEqual(check.gaps, [])

    def test_cardinality_rejects_default_value_even_when_null(self) -> None:
        for value in ("null", "false"):
            body = CARDINALITY.replace(
                "condition:\n", f"default_value: {value}\ncondition:\n"
            )
            with self.subTest(value=value):
                check = self.validate(body)
                self.assertTrue(check.findings)
                self.assertEqual(check.gaps, [])

    def test_cardinality_extraction_preserves_exact_yaml_and_crlf(
        self,
    ) -> None:
        body = CARDINALITY.replace("maximum: 1", "maximum: null")
        for source in (body, body.replace("\n", "\r\n")):
            with self.subTest(crlf="\r\n" in source):
                check = Recorder()
                extracted = validated_graph_rule_payload(
                    source,
                    check,  # type: ignore[arg-type]
                )
                self.assertEqual(check.findings, [])
                self.assertEqual(check.gaps, [])
                assert extracted is not None
                opening = source.index("```yaml")
                closing = source.index("```", opening + 3)
                closing_end = source.index("\n", closing) + 1
                self.assertEqual(
                    extracted.operative_yaml,
                    source[source.index("\n", opening) + 1 : closing],
                )
                self.assertEqual(
                    extracted.operative_block, source[opening:closing_end]
                )
                self.assertEqual(
                    extracted.payload["graph_rule_type"], "cardinality"
                )
                self.assertIsNone(extracted.payload["condition"]["maximum"])


if __name__ == "__main__":
    unittest.main()
