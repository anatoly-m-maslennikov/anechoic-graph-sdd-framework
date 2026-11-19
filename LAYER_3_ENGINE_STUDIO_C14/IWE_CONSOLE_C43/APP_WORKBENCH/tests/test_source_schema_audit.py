import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

WORKBENCH = Path(__file__).resolve().parents[1]
TOOLS = WORKBENCH.parents[1] / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS'
sys.path[:0] = [str(WORKBENCH), str(TOOLS)]

from ATOM_LIFECYCLE.candidate_schema import CandidateSchema
from ATOM_LIFECYCLE.content_constraints import compile_content_constraints, load_content_constraints
from ATOM_LIFECYCLE.header_constraints import compile_header_constraints, load_header_constraints
from ATOM_LIFECYCLE.role_form_schema import RoleFormSchema
from ATOM_LIFECYCLE.status_model import StatusModel
from FEATURE_WORKBENCH_BACKEND.content_schema import compile_content_schema
from FEATURE_WORKBENCH_BACKEND.header_columns import HeaderColumn, HeaderSchema
from FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content
from FEATURE_WORKBENCH_BACKEND.source_schema_audit import SourceSchemaAudit


def declaration(number, name, base_path, extra="", *, values=1):
    reference = f"CA-R-{number}"
    body = (
        "## Claim\n### Formal Claim\n```python\n"
        "from anechoic.formal_claims import Cardinality, declare_entity\n"
        "from anechoic.model import Concern\n"
        f'declare_entity(entity_name={name!r}, relation_name="IS_PROPERTY_OF", base_path={base_path!r}, '
        f'property_occurrence_cardinality=1, value_cardinality={values}, {extra})\n```\n'
    ).encode()
    return {'id': reference, 'ref': reference, 'source_path': f'{reference}.md',
            'version': 1, 'status_group': 'Current', 'role': 'Requirement',
            'form': 'Declaration', '_content_bytes': body}


def auditor():
    declarations = [
        declaration(1, "Role", "Atom.Header", "value_format=str"),
        declaration(2, "Status", "Atom.Header", "value_format=str"),
        declaration(3, "Version", "Atom.Header", "value_format=int"),
        declaration(4, "Priority", "Atom.Header",
                    'value_format=str, applies_to_entity_classes=(Concern,), allowed_values=("High",)'),
        declaration(5, "Summary", "Atom.Content"),
        declaration(6, "Claim", "Atom.Content",
                    'dependent_property_cardinality=Cardinality(minimum=1, maximum=2), '
                    'allowed_dependent_property_names=("Formal Claim", "Prose Claim")', values=0),
    ]
    source_ids = {row['id'] for row in declarations}
    content = compile_content_schema(declarations)
    header = HeaderSchema((HeaderColumn(('version',), 'header.version', 'BIGINT', True, 'version'),))
    roles = RoleFormSchema(frozenset({'Concern', 'Requirement'}), frozenset({'Problem', 'Declaration'}),
                           frozenset(), ())
    schema = CandidateSchema(SimpleNamespace(header=lambda _mode: header, content=content), roles,
                             load_header_constraints(compile_header_constraints(declarations), source_ids),
                             load_content_constraints(compile_content_constraints(declarations), source_ids))
    status = StatusModel(((None, None, 'Active'), (None, None, 'Archived')))
    return SourceSchemaAudit(schema, status)


def atom(header, body, group='Current'):
    return {'source_path': 'some/atom.md', 'status_group': group, 'header_json': header,
            'role': header.get('role'), 'form': header.get('form'), '_content_bytes': body.encode(),
            'content_properties_json': parse_content(body, tolerate_duplicate_siblings=True, compact=True)}



class Tests(unittest.TestCase):
    def test_valid_row_and_archived_row_are_both_audited_without_reparsing(self):
        audit = auditor()
        body = '## Summary\nExample\n## Claim\n### Prose Claim\nText\n'
        header = {'role': 'concern', 'form': 'problem', 'status': 'active', 'version': 1, 'priority': 'High'}
        current = atom(header, body)
        archived = atom({**header, 'status': 'archived', 'priority': 'Wrong'}, body, 'Archived')
        with patch('FEATURE_WORKBENCH_BACKEND.markdown_content.parse_content', side_effect=AssertionError('reparsed')):
            assert audit.issues(current) == []
            assert any(issue['field'] == 'priority' for issue in audit.issues(archived))


    def test_reports_multiple_header_and_content_violations(self):
        audit = auditor()
        row = atom({'role': 'concern', 'form': 'problem', 'status': 'bad', 'version': 'wrong'},
                   '## Summary\n## Claim\n### Unexpected\nText\n')
        issues = audit.issues(row)
        assert {'status', 'header.version', 'priority', 'content.summary', 'content.claim'} <= {
            issue['field'] for issue in issues}


    def test_reports_duplicate_declared_fields_in_archived_sources(self):
        audit = auditor()
        row = atom({'role': 'concern', 'form': 'problem', 'status': 'archived', 'version': 1, 'priority': 'High'},
                   '## Summary\nOne\n## Summary\nTwo\n## Claim\n### Prose Claim\nText\n', 'Archived')
        issues = audit.issues(row)
        assert any('duplicate declared content property: summary' in issue['message'] for issue in issues)


    def test_required_heading_and_direct_values_are_independent(self):
        audit = auditor()
        row = atom({'role': 'concern', 'form': 'problem', 'status': 'active', 'version': 1, 'priority': 'High'},
                   '## Summary\n## Claim\n### Prose Claim\nText\n')
        issues = audit.issues(row)
        assert any(issue['field'] == 'content.summary' and 'direct Markdown values' in issue['message'] for issue in issues)


    def test_null_is_not_a_valid_integer_even_when_property_is_present(self):
        audit = auditor()
        row = atom({'role': 'concern', 'form': 'problem', 'status': 'active', 'version': None, 'priority': 'High'},
                   '## Summary\nText\n## Claim\n### Prose Claim\nText\n')
        assert any(issue['field'] == 'header.version' for issue in audit.issues(row))


    def test_undeclared_form_is_reported(self):
        audit = auditor()
        row = atom({'role': 'concern', 'form': 'not_declared', 'status': 'active', 'version': 1, 'priority': 'High'},
                   '## Summary\nText\n## Claim\n### Prose Claim\nText\n')
        assert any(issue['field'] == 'form' for issue in audit.issues(row))
