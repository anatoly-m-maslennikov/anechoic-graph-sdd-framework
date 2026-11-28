"""Publish Component metrics."""


def replace_component_metrics(connection, measurements) -> None:
    """Publish three Spec ratios per Component and Realization denominator."""
    connection.execute(
        """CREATE OR REPLACE TABLE main.component_metrics AS
        WITH sizes AS (
            SELECT unnest(?::VARCHAR[]) AS component_id,
                   unnest(?::BIGINT[]) AS spec_full_bytes,
                   unnest(?::BIGINT[]) AS spec_body_bytes,
                   unnest(?::BIGINT[]) AS spec_body_lines,
                   unnest(?::BIGINT[]) AS implementation_bytes,
                   unnest(?::BIGINT[]) AS implementation_lines,
                   unnest(?::BIGINT[]) AS test_code_bytes,
                   unnest(?::BIGINT[]) AS test_code_lines,
                   unnest(?::BIGINT[]) AS test_asset_bytes,
                   unnest(?::BIGINT[]) AS test_asset_lines
        )
        SELECT component_id, denominator,
               spec_full_bytes / 1000 AS spec_full_kb,
               spec_body_bytes / 1000 AS spec_body_kb,
               spec_body_lines,
               code_bytes / 1000 AS realization_kb,
               code_lines AS realization_lines,
               spec_full_bytes / nullif(code_bytes, 0) AS spec_full_kb_ratio,
               spec_body_bytes / nullif(code_bytes, 0) AS spec_body_kb_ratio,
               spec_body_lines / nullif(code_lines, 0) AS spec_body_lines_ratio
        FROM sizes, LATERAL (VALUES
            ('implementation', implementation_bytes, implementation_lines),
            ('test_code', test_code_bytes, test_code_lines),
            ('test_assets', test_asset_bytes, test_asset_lines),
"""
        "            ('tests', test_code_bytes + test_asset_bytes, "
        "test_code_lines + test_asset_lines),\n"
        "            ('implementation_and_tests', implementation_bytes + "
        "test_code_bytes + test_asset_bytes,\n"
        "             implementation_lines + test_code_lines + "
        "test_asset_lines)\n"
        "        ) AS population(denominator, code_bytes, code_lines)\n"
        "        ",
        [[row[index] for row in measurements] for index in range(10)],
    )
