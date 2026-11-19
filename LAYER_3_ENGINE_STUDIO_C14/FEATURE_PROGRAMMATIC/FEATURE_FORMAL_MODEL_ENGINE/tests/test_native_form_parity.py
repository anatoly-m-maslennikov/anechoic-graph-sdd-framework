from pathlib import Path
import sys
import unittest

FEATURE = Path(__file__).resolve().parents[1]
PROGRAMMATIC = FEATURE.parent
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / 'FEATURE_TOOLS'), str(PROGRAMMATIC.parent / 'IWE_CONSOLE_C43/APP_WORKBENCH')]

from ATOM_LIFECYCLE.role_form_schema import compile_role_form  # noqa: E402
from ATOM_LIFECYCLE.content_constraints import compile_content_constraints  # noqa: E402
from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim  # noqa: E402


def row(source, claim, language='CFEL'):
    body = f'## Claim\n\n### Formal Claim\n\n```{language}\n{claim}\n```\n'
    return {'id': source, 'ref': source, 'version': 1, 'source_path': 'source.md',
            'status_group': 'Current', 'role': 'Requirement', 'form': 'Declaration',
            '_content_bytes': body.encode(), 'content_markdown': body}


class NativeFormParityTests(unittest.TestCase):
    def test_role_and_content_consumers_match(self):
        examples = [
            ('''Atom.Header.Context.Form :: Scope Delegation;
FOR EACH $a[<Atom>, (.Header.Context.Form = Scope Delegation)]:
($a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1});''',
             '''from anechoic.formal_claims import declare_entity
declare_entity(entity_name='Form', relation_name='IS_PROPERTY_OF', base_path='Atom.Header.Context',
    allowed_values=('Scope Delegation',), form_roles=('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'))'''),
            ('''Atom.Header.Context.Form :: Work Report;
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details:: {::1};
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details.*[]{::0};
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Summary ;> Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details;
FOR EACH $report[<Atom>, (.Header.Context.Form = Work Report)]: ($report.Header.Context.Role == Plan);''',
             '''from anechoic.formal_claims import declare_entity
from anechoic.model import Plan
class WorkReport(Plan):
    pass
declare_entity(entity_name='Work Report', entity_class=WorkReport, qualification_property_path='Atom.Header.Context.Form',
    form_roles=('Plan',), form_content={'required_value': 'Details', 'no_children': 'Details', 'after': 'Summary'})''')]
        self.assertEqual([], compile_content_constraints([row('R', examples[0][1], 'python')]))
        self.assertEqual(
            {('value', ('details',), 1, 1, ()), ('children', ('details',), 0, 0, ()),
             ('order', (), 0, 0, ('summary', 'details'))},
            {(item['kind'], tuple(item['path']), item['min'], item['max'], tuple(item['children']))
             for item in compile_content_constraints([row('R', examples[1][1], 'python')])},
        )
        self.assertEqual(
            {('form', 'Scope Delegation', ''),
             *(('constraint', 'Scope Delegation', role) for role in
               ('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'))},
            {(item['kind'], item['value'], item['role'])
             for item in compile_role_form([row('R', examples[0][1], 'python')])},
        )
        self.assertEqual(
            {('form', 'Work Report', ''), ('constraint', 'Work Report', 'Plan')},
            {(item['kind'], item['value'], item['role'])
             for item in compile_role_form([row('R', examples[1][1], 'python')])},
        )
        with self.assertRaises(ValueError):
            parse_native_model_claim(examples[0][1].replace("('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations')", "()"))

    def test_workflow_content_projection_keeps_form_ancestry(self):
        new = row('workflow', '''from anechoic.formal_claims import declare_entity
from anechoic.model import Operations
class Workflow(Operations):
    pass
declare_entity(entity_name='Workflow', entity_class=Workflow, qualification_property_path='Atom.Header.Context.Form', project_form_content=True)''', 'python')
        content = row('content', '''from anechoic.formal_claims import declare_entity
declare_entity(entity_name='Claim', relation_name='IS_PROPERTY_OF', base_path='Workflow.Content',
    property_occurrence_cardinality=1, value_cardinality=1)''', 'python')
        result = compile_content_constraints([new, content])
        self.assertEqual({'heading', 'heading_value'}, {item['kind'] for item in result})
        for item in result:
            self.assertEqual((['claim'], ['Operations'], ['Workflow'], 1, 1),
                             (item['path'], item['roles'], item['forms'], item['min'], item['max']))


if __name__ == '__main__':
    unittest.main()
