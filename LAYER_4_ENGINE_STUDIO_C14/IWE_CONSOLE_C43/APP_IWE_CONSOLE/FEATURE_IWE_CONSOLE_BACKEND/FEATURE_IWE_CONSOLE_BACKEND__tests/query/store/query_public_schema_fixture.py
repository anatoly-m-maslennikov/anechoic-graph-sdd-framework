"""Expected ordering of public Workbench schema columns."""

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import SCOPE_FIELDS


ISSUE_TABLES = (
    "atom_declared_carrier_issues",
    "atom_duplicate_revision_issues",
    "atom_parse_issues",
    "atom_physical_carrier_issues",
    "atom_schema_issues",
)
ISSUE_FIELDS = (
    "reference",
    "relative_path",
    "filename",
    "issue_category",
    "property",
    "observed",
    "expected",
    "diagnostic",
)
FIELD_GROUPS = {
    "change_log": ("observed_at", "operation", "old_path", "new_path"),
    "live_runs": ("run_id", "session_id", "tool", "status"),
    "query_log": (
        "log_id",
        "at",
        "sql",
        "outcome",
        "error",
        "row_count",
        "column_count",
    ),
    "query_log_records": (
        "log_id",
        "at",
        "sql",
        "outcome",
        "error",
        "row_count",
        "column_count",
    ),
    "relations": (
        "source_kind",
        "source_ref",
        "target_kind",
        "target_ref",
        "relation_type",
        "derived",
    ),
    "runtime_diagnostics": (
        "observed_at",
        "name",
        "outcome",
        "returned_outcome",
        "error_category",
        "project_prefix",
        "project_instance_id",
    ),
    "scope_units": SCOPE_FIELDS,
}


def expected_public_schema(atom_fields):
    return (
        [[table, field] for table in ISSUE_TABLES for field in ISSUE_FIELDS]
        + [["atoms", field] for field in atom_fields]
        + [
            [table, field]
            for table, names in FIELD_GROUPS.items()
            for field in names
        ]
    )
