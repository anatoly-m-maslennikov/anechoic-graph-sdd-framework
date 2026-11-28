import unittest
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.FEATURE_TOOLS__tests__shared import (
    compile_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle._candidate_schema_read import (
    load_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_content,
)
# fmt: on
from .legacy_source_schema_audit import SourceSchemaAudit

WORKBENCH = Path(__file__).resolve().parents[4]
TOOLS = WORKBENCH.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"


def declaration(number, name, base_path, extra="", *, values=1):
    reference = f"CA-R-{number}"
    body = (
        "## Claim\n### Formal Claim\n```python\n"
        "from anechoic.formal_claims import Cardinality, declare_entity\n"
        "from anechoic.model import Concern\n"
        f"declare_entity(entity_name={name!r}, "
        f'relation_name="IS_PROPERTY_OF", base_path={base_path!r}, '
        f"property_occurrence_cardinality=1, value_cardinality={values}, "
        f"{extra})\n```\n"
    ).encode()
    return {
        "id": reference,
        "ref": reference,
        "source_path": f"{reference}.md",
        "version": 1,
        "status_group": "Current",
        "role": "Requirement",
        "form": "Declaration",
        "_content_bytes": body,
    }


def _compile_fixture_schema(declarations):
    role_claims = (
        ("Concern", "Atom", "Atom.Header.Context.Role"),
        ("Requirement", "Atom", "Atom.Header.Context.Role"),
        ("Problem", "Concern", "Atom.Header.Context.Form"),
        ("Declaration", "Requirement", "Atom.Header.Context.Form"),
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "model"
        root.mkdir()
        for row in declarations:
            header = (
                f"---\natom_id: {row['id']}\nrole: Requirement\n"
                "form: Declaration\n"
                "status: Active\nversion: 1\n---\n"
            )
            (root / row["source_path"]).write_bytes(
                header.encode() + row["_content_bytes"]
            )
        for index, (name, base, qualification) in enumerate(role_claims, 20):
            (root / f"CA-R-{index}.md").write_text(
                f"---\natom_id: CA-R-{index}\nrole: Requirement\n"
                "form: Declaration\n"
                "status: Active\nversion: 1\n---\n"
                "## Claim\n### Formal Claim\n```python\n"
                f"from anechoic.model import {base}\n"
                f"class {name}({base}):\n    pass\n"
                "from anechoic.formal_claims import declare_entity\n"
                f'declare_entity(entity_name="{name}", entity_class={name}, '
                f'qualification_property_path="{qualification}")\n```\n',
                encoding="utf-8",
            )
        asset = Path(directory) / "schema.json"
        asset.write_bytes(compile_candidate_schema(root))
        schema = load_candidate_schema(asset)
    return schema


def auditor(*, container_constraint=False):
    declarations = [
        declaration(1, "Role", "Atom.Header", "value_format=str"),
        declaration(2, "Status", "Atom.Header", "value_format=str"),
        declaration(3, "Version", "Atom.Header", "value_format=int"),
        declaration(
            4,
            "Priority",
            "Atom.Header",
            "value_format=str, applies_to_entity_classes=(Concern,), "
            'allowed_values=("High",)',
        ),
        declaration(5, "Summary", "Atom.Content"),
        declaration(
            6,
            "Claim",
            "Atom.Content",
            "dependent_property_cardinality="
            "Cardinality(minimum=1, maximum=2), "
            'allowed_dependent_property_names=("Formal Claim", "Prose Claim")',
            values=0,
        ),
    ]
    if container_constraint:
        container = declaration(
            2779,
            "Container",
            "Atom.Header",
            "dependent_property_cardinality=1, "
            'allowed_dependent_property_names=("atom", "scope_unit")',
            values=0,
        )
        container["_content_bytes"] = container["_content_bytes"].replace(
            b"value_cardinality=0, ", b""
        )
        declarations.append(container)
    schema = _compile_fixture_schema(declarations)
    status = SimpleNamespace(
        allowed=lambda _role, _form: frozenset({"Active", "Archived"})
    )
    return SourceSchemaAudit(schema, status)


def atom(header, body, group="Current"):
    return {
        "source_path": "some/atom.md",
        "status_group": group,
        "header_json": header,
        "role": header.get("role"),
        "form": header.get("form"),
        "_content_bytes": body.encode(),
        "content_properties_json": parse_content(
            body, tolerate_duplicate_siblings=True, compact=True
        ),
    }


class Tests(unittest.TestCase):
    def test_valid_row_and_archived_row_are_both_audited_without_reparsing(
        self,
    ):
        audit = auditor()
        body = "## Summary\nExample\n## Claim\n### Prose Claim\nText\n"
        header = {
            "role": "concern",
            "form": "problem",
            "status": "active",
            "version": 1,
            "priority": "High",
        }
        current = atom(header, body)
        archived = atom(
            {**header, "status": "archived", "priority": "Wrong"},
            body,
            "Archived",
        )
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "ADAPTERS_C30__shared.parse_content",
            side_effect=AssertionError("reparsed"),
        ):
            assert audit.issues(current) == []
            assert any(
                issue["field"] == "priority"
                for issue in audit.issues(archived)
            )

    def test_reports_multiple_header_and_content_violations(self):
        audit = auditor()
        row = atom(
            {
                "role": "concern",
                "form": "problem",
                "status": "bad",
                "version": "wrong",
            },
            "## Summary\n## Claim\n### Unexpected\nText\n",
        )
        issues = audit.issues(row)
        assert {
            "status",
            "header.state.version",
            "priority",
            "content.summary",
            "content.claim",
        } <= {issue["field"] for issue in issues}

    def test_reports_duplicate_declared_fields_in_archived_sources(self):
        audit = auditor()
        row = atom(
            {
                "role": "concern",
                "form": "problem",
                "status": "archived",
                "version": 1,
                "priority": "High",
            },
            "## Summary\nOne\n## Summary\nTwo\n"
            "## Claim\n### Prose Claim\nText\n",
            "Archived",
        )
        issues = audit.issues(row)
        assert any(
            "duplicate declared content property: summary" in issue["message"]
            for issue in issues
        )

    def test_required_heading_and_direct_values_are_independent(self):
        audit = auditor()
        row = atom(
            {
                "role": "concern",
                "form": "problem",
                "status": "active",
                "version": 1,
                "priority": "High",
            },
            "## Summary\n## Claim\n### Prose Claim\nText\n",
        )
        issues = audit.issues(row)
        assert any(
            issue["field"] == "content.summary"
            and "direct Markdown values" in issue["message"]
            for issue in issues
        )

    def test_null_is_not_a_valid_integer_even_when_property_is_present(self):
        audit = auditor()
        row = atom(
            {
                "role": "concern",
                "form": "problem",
                "status": "active",
                "version": None,
                "priority": "High",
            },
            "## Summary\nText\n## Claim\n### Prose Claim\nText\n",
        )
        assert any(
            issue["field"] == "header.state.version"
            for issue in audit.issues(row)
        )

    def test_undeclared_form_is_reported(self):
        audit = auditor()
        row = atom(
            {
                "role": "concern",
                "form": "not_declared",
                "status": "active",
                "version": 1,
                "priority": "High",
            },
            "## Summary\nText\n## Claim\n### Prose Claim\nText\n",
        )
        assert any(issue["field"] == "form" for issue in audit.issues(row))
