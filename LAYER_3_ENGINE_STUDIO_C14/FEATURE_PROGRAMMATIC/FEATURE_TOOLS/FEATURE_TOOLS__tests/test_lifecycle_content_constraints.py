import sys
from pathlib import Path
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
WORKBENCH = TOOLS.parent.parent / 'IWE_CONSOLE_C43/APP_WORKBENCH'
sys.path[:0] = [str(TOOLS), str(WORKBENCH)]
from ATOM_LIFECYCLE.content_constraints import compile_content_constraints, load_content_constraints  # noqa: E402


def declaration(ref, code):
    return {'status_group': 'Current', 'role': 'Requirement', 'form': 'Declaration',
            'id': ref, 'ref': ref, 'version': 1, 'source_path': ref + '.md',
            '_content_bytes': ('## Claim\n### Formal Claim\n```python\n'
                               'from anechoic.formal_claims import Cardinality, declare_entity\n'
                               + code + '\n```\n').encode()}


class ContentConstraintsTests(unittest.TestCase):
    def test_native_order_and_declared_children(self):
        rows = [
            declaration('CA-R-1', 'declare_entity(entity_name="Content", relation_name="IS_PROPERTY_OF", base_path="Atom", ordered_dependent_property_pairs=(("Summary", "Claim"), ("Claim", "Details")))'),
            declaration('CA-R-2', 'declare_entity(entity_name="Summary", relation_name="IS_PROPERTY_OF", base_path="Atom.Content", property_occurrence_cardinality=1, value_cardinality=1, dependent_property_cardinality=0)'),
            declaration('CA-R-3', 'declare_entity(entity_name="Governed", relation_name="IS_PROPERTY_OF", base_path="Atom.Content.Summary", value_cardinality=1)'),
        ]
        schema = load_content_constraints(compile_content_constraints(rows), {row['id'] for row in rows})
        def check(body):
            schema.validate({'role': 'Plan', 'form': 'Plan', 'content_markdown': body})
        check('## Summary\n### Presentation\nText\n## Structure\n### A\nText\n## Details\nText\n')
        with self.assertRaisesRegex(ValueError, 'out of order'):
            check('## Details\nText\n## Summary\nText\n')
        with self.assertRaisesRegex(ValueError, 'children'):
            check('## Summary\nText\n### Governed\nText\n')
        with self.assertRaisesRegex(ValueError, 'direct Markdown'):
            check('## Summary\n')

    def test_native_qualified_content_compiles_without_translation(self):
        row = declaration('CA-R-1', "declare_entity(entity_name='Mermaid Scheme', relation_name='IS_PROPERTY_OF', "
            "base_path='Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step).Content.Claim', "
            "property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), "
            "value_format='markdown', value_cardinality=1, dependent_property_cardinality=0)")
        with patch('python_model_claim.compile_python_model_claim', side_effect=AssertionError('translated')):
            records = compile_content_constraints([row])
        self.assertEqual({'heading', 'heading_value', 'children'}, {item['kind'] for item in records})
        self.assertTrue(all(item['roles'] == ['Operations'] and item['forms'] == ['Step'] for item in records))

    def test_named_form_content_compiles_without_translation(self):
        rows = [
            declaration('CA-R-1', "from anechoic.model import Operations\nclass Workflow(Operations):\n    pass\ndeclare_entity(entity_name='Workflow', entity_class=Workflow, qualification_property_path='Atom.Header.Context.Form', project_form_content=True)"),
            declaration('CA-R-2', "declare_entity(entity_name='Mermaid Scheme', relation_name='IS_PROPERTY_OF', base_path='Workflow.Content.Claim', property_occurrence_cardinality=1, value_cardinality=1, value_format='markdown', dependent_property_cardinality=0)"),
            declaration('CA-R-3', "from anechoic.model import Plan\nclass WorkReport(Plan):\n    pass\ndeclare_entity(entity_name='Work Report', entity_class=WorkReport, qualification_property_path='Atom.Header.Context.Form', form_roles=('Plan',), form_content={'required_value': 'Details', 'no_children': 'Details', 'after': 'Summary'})"),
        ]
        with patch('python_model_claim.compile_python_model_claim', side_effect=AssertionError('translated')):
            records = compile_content_constraints(rows)
        workflow = [r for r in records if r['source'] == 'CA-R-2']
        self.assertEqual({'heading', 'heading_value', 'children'}, {r['kind'] for r in workflow})
        self.assertTrue(all(r['roles'] == ['Operations'] and r['forms'] == ['Workflow'] for r in workflow))
        report = [r for r in records if r['source'] == 'CA-R-3']
        self.assertEqual({'value', 'children', 'order'}, {r['kind'] for r in report})
        self.assertTrue(all(r['roles'] == ['Plan'] and r['forms'] == ['Work Report'] for r in report))

    def test_prose_heading_is_markdown_not_a_property(self):
        row = declaration('CA-R-1', "from anechoic.model import Requirement\ndeclare_entity(entity_name='Prose Claim', relation_name='IS_PROPERTY_OF', base_path='Atom.Content.Claim', applies_to_entity_classes=(Requirement,), value_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=0)")
        schema = load_content_constraints(compile_content_constraints([row]), {'CA-R-1'})
        schema.validate({'role': 'Requirement', 'form': 'Declaration',
                         'content_markdown': '## Claim\n### Prose Claim\n#### Applicability\nText\n'})

    def test_untrusted_asset_is_checked(self):
        with self.assertRaises(ValueError):
            load_content_constraints([{'path': ['summary'], 'roles': None, 'forms': None,
                'min': 1, 'max': 1, 'children': [], 'source': 'CA-R-unknown'}], {'CA-R-1'})


if __name__ == '__main__':
    unittest.main()
