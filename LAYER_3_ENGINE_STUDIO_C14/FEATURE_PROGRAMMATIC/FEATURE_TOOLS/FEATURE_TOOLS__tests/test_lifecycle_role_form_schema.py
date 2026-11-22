from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent.parent / 'IWE_CONSOLE_C43/APP_WORKBENCH'))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.role_form_schema import compile_role_form, load_role_form  # noqa: E402


def row(source, claim):
    return {'id': source, '_content_bytes': f'## Claim\n### Formal Claim\n```python\n{claim}\n```\n'.encode()}


def role(name, cls):
    return (f'from anechoic.formal_claims import declare_entity\n'
            f'class {cls}:\n    pass\n'
            f'declare_entity(entity_name={name!r}, entity_class={cls}, '
            f'qualification_property_path="Atom.Header.Context.Role")')


def form(name, cls, base, extra=''):
    return (f'from anechoic.formal_claims import declare_entity\n'
            f'from anechoic.model import {base}\nclass {cls}({base}):\n    pass\n'
            f'declare_entity(entity_name={name!r}, entity_class={cls}, '
            f'qualification_property_path="Atom.Header.Context.Form"{extra})')


class RoleFormCompilationTests(unittest.TestCase):
    def test_native_roles_qualified_forms_and_cross_role_constraints(self):
        sources = [row('R1', role('Analysis and Advisory', 'AnalysisAndAdvisory')),
                   row('R2', role('Method', 'Method')),
                   row('R3', form('Decision', 'MethodDecision', 'Method')),
                   row('R4', form('Report', 'Report', 'AnalysisAndAdvisory',
                                  ', form_roles=("Analysis and Advisory",)'))]
        result = compile_role_form(sources)
        self.assertEqual({('role', 'Analysis and Advisory', ''), ('role', 'Method', ''),
                          ('qualified', 'Decision', 'Method'), ('form', 'Report', ''),
                          ('constraint', 'Report', 'Analysis and Advisory')},
                         {(item['kind'], item['value'], item['role']) for item in result})
        schema = load_role_form(result, {'R1', 'R2', 'R3', 'R4'})
        schema.validate('Method', 'Decision')
        with self.assertRaisesRegex(ValueError, 'not permitted'):
            schema.validate('Analysis and Advisory', 'Decision')

    def test_property_form_roles_and_unknown_role_base(self):
        claim = ('from anechoic.formal_claims import declare_entity\n'
                 'declare_entity(entity_name="Form", relation_name="IS_PROPERTY_OF", '
                 'base_path="Atom.Header.Context", allowed_values=("Scope Delegation",), '
                 'form_roles=("Method",))')
        records = compile_role_form([row('R1', claim)])
        self.assertEqual({'form', 'constraint'}, {item['kind'] for item in records})
        with self.assertRaisesRegex(ValueError, 'declared Role base class'):
            compile_role_form([row('R2', form('Decision', 'MethodDecision', 'Method'))])

    def test_form_inherits_role_through_another_declared_class(self):
        parent = ('from anechoic.formal_claims import declare_entity\n'
                  'from anechoic.model import Method\nclass Intermediate(Method):\n    pass\n'
                  'declare_entity(entity_name="Intermediate", entity_class=Intermediate)')
        records = compile_role_form([row('R1', role('Method', 'Method')), row('R2', parent),
                                     row('R3', form('Decision', 'MethodDecision', 'Intermediate'))])
        self.assertIn({'kind': 'qualified', 'value': 'Decision', 'role': 'Method', 'source': 'R3'}, records)


if __name__ == '__main__':
    unittest.main()
