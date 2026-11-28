"""Additional Graph Rule body cases shared with the main test class."""

from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.VALIDATE_ATOMS.\
    validate_atoms_workers.validate_atoms_workers__shared import (
    validated_graph_rule_payload,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import CEILINGS  # fmt: skip
from graph_rule_body_test_support import Recorder, WHITELIST


class EncodeTrap(str):
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        raise AssertionError("oversized body must be rejected before encoding")


class GraphRuleBodyMoreTests:
    def test_malformed_subject_notation_fails(self) -> None:
        for subject in ('"Entity///Atom"', "'atom(type=\"Plan\").Status'"):
            body = WHITELIST.replace(
                '"Entity/Node/Continuant/Atom/Content Role: Evaluation"',
                subject,
            )
            with self.subTest(subject=subject):
                self.assertTrue(self.validate(body).findings)

    def test_extra_sections_and_trailing_prose_fail(self) -> None:
        for body in (
            WHITELIST.replace("```yaml", "## Claim\nDuplicate.\n\n```yaml"),
            WHITELIST + "Trailing prose.\n",
            WHITELIST.replace("```yaml", "```text", 1),
        ):
            with self.subTest(body=body):
                self.assertTrue(self.validate(body).findings)

    def test_commonmark_fences_and_leading_blank_lines_pass(self) -> None:
        bodies = (
            "\n\n" + WHITELIST,
            WHITELIST.replace("```yaml", "  ````yaml").replace(
                "\n```\n", "\n  ````   \n"
            ),
            WHITELIST.replace("```yaml", "~~~yaml").replace(
                "\n```\n", "\n~~~\n"
            ),
        )
        for body in bodies:
            with self.subTest(body=body):
                check = self.validate(body)
                self.assertEqual(check.findings, [])
                self.assertEqual(check.gaps, [])

    def test_body_byte_limit_accepts_exact_boundary_and_counts_utf8_bytes(
        self,
    ) -> None:
        body = WHITELIST.replace(
            "Allow evaluation links.", "Allow evaluation 🌉."
        )
        byte_size = len(body.encode("utf-8"))
        self.assertGreater(byte_size, len(body))
        with patch.dict(CEILINGS, {"max_file_bytes": byte_size}):
            self.assertEqual(self.validate(body).findings, [])
        with patch.dict(CEILINGS, {"max_file_bytes": len(body)}):
            check = self.validate(body)
        self.assertEqual(check.findings[0][1], "body")
        self.assertIn("byte ceiling", check.findings[0][2])

    def test_oversized_character_count_is_rejected_before_encoding(
        self,
    ) -> None:
        with patch.dict(CEILINGS, {"max_file_bytes": 1}):
            check = self.validate(EncodeTrap(WHITELIST))
        self.assertIn("byte ceiling", check.findings[0][2])

    def test_unencodable_body_fails_with_sanitized_diagnostic(self) -> None:
        check = self.validate(WHITELIST + "\ud800")
        self.assertEqual(check.findings[0][1], "body")
        self.assertNotIn("\ud800", check.findings[0][2])

    def test_other_declared_type_is_a_gap_not_a_guessed_schema(self) -> None:
        body = WHITELIST.replace(
            "graph_rule_type: whitelist", "graph_rule_type: blacklist"
        )
        check = self.validate(body)
        self.assertEqual(check.findings, [])
        self.assertEqual(len(check.gaps), 1)
        extraction_check = Recorder()
        extracted = validated_graph_rule_payload(
            body,
            extraction_check,  # type: ignore[arg-type]
        )
        self.assertIsNone(extracted)
        self.assertEqual(extraction_check.findings, [])
        self.assertEqual(len(extraction_check.gaps), 1)
