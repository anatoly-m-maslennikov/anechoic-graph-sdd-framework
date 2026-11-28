"""Shared source fixtures for the Methodology compiler tests."""

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared \
    import write_scope_unit_declarations  # fmt: skip


def write_methodology_scope(root):
    return write_scope_unit_declarations(
        root,
        (
            {
                "scope_unit_name": "METHODOLOGY_SOURCES",
                "parent": "PROJECT",
                "scope_unit_type": "Unordered",
            },
            {
                "scope_unit_name": "CORE_META_MODEL",
                "parent": "METHODOLOGY_SOURCES",
                "scope_unit_type": "Unordered",
            },
            {
                "scope_unit_name": "INSTALLED_EXTENSIONS",
                "parent": "METHODOLOGY_SOURCES",
                "scope_unit_type": "Unordered",
            },
            {
                "scope_unit_name": "PROJECT_CONFIGURATION",
                "parent": "METHODOLOGY_SOURCES",
                "scope_unit_type": "Unordered",
            },
        ),
    )


NESTED_RULE = (
    b"---\nidentity:\n  atom_id: CA-R-001\n  ref_id: CA-R-001@2\n"
    b"context:\n  role: Requirement\n  form: Rule\n  topics:\n"
    b"    main_subject: Header\n    dependencies: []\n"
    b"relations: {}\nstate:\n  status: Active\n  version: 2\n"
    b'  updated_at: "2026-11-06 00:00:00 +0400"\n'
    b"destination:\n  file:\n    name: CA-R-001--nested\n"
    b"    path: preserved/path\n"
    b"---\n# Claim\n\nExact nested source body.\n"
)
