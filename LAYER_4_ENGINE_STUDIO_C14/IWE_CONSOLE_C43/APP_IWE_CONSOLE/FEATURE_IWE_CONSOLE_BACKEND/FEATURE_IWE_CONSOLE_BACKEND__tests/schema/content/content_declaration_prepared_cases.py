"""Prepared content schema coverage."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_content,
)


class PreparedContentCases:
    def test_prepared_header_grouping_keeps_the_real_content_schema(
        self,
    ) -> None:
        rows = self._current_model_rows()
        before = self._compile_model_rows(rows)
        transform = self._prepared_reference_transform()
        prepared = []
        for row in rows:
            body = transform(row["content_markdown"])
            prepared.append(
                {
                    **row,
                    "content_markdown": body,
                    "_content_bytes": body.encode("utf-8"),
                    "content_properties_json": parse_content(
                        body, tolerate_duplicate_siblings=True
                    ),
                }
            )

        after = self._compile_model_rows(prepared)
        claim_rules = [
            rule
            for rule in after.rules
            if rule.source.reference == "CA-R-2500"
        ]
        self.assertTrue(claim_rules)
        self.assertEqual(
            {frozenset({"Requirement", "Method", "Evaluation", "Delivery"})},
            {rule.roles for rule in claim_rules},
        )
        self.assertEqual(before.shape, after.shape)
