import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.legacy_candidate_schema__pub import compile_candidate_schema, load_candidate_schema  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.role_form_schema import RoleFormSchema  # noqa: E402

CORE = Path(__file__).parent / 'assets/lifecycle_schema_declarations'


def source(atom_id, status='Active', body=''):
    return f'''---
atom_id: {atom_id}
role: Requirement
form: Declaration
status: {status}
version: 1
---
{body}
'''



def _formal_fixture_source():
    encoded = source('CA-R-1', status='active', body='''## Claim
### Formal Claim
```CFEL
# a comment is not a gate
Atom.Header.Role :: Plan;
Atom.Header.Role :: Method;
Atom.Header.Form :: Decision;
# Atom.Header.Role :: Phantom;
Atom/(.Header.Role in (Plan)).Header.Form :: Plan;
FOR EACH $a[<Atom>, (.Header.Form = Decision)]:
(
    $a.Header.Role:: [in (Method)]{::1}
);
Atom.Header.ID:: [atom id]{::1};
Atom.Content.Summary:: {::1}; # inline comment
# Atom.Content.Secret:: {::1};
```
## Other
```CFEL
Atom.Content.Hidden:: {::1};
```
''')
    return encoded


def _native_claim_fixtures():
    native_claims = {
        'CA-R-4': '''from anechoic.model import Atom
class Plan(Atom):
    pass
declare_entity(entity_name="Plan", entity_class=Plan,
       qualification_property_path="Atom.Header.Context.Role")''',
        'CA-R-5': '''from anechoic.model import Atom
class Method(Atom):
    pass
declare_entity(entity_name="Method", entity_class=Method,
       qualification_property_path="Atom.Header.Context.Role")''',
        'CA-R-6': '''from anechoic.model import Plan
class PlanForm(Plan):
    pass
declare_entity(entity_name="Plan", entity_class=PlanForm,
       qualification_property_path="Atom.Header.Context.Form")''',
        'CA-R-7': '''declare_entity(entity_name="Form", relation_name="IS_PROPERTY_OF",
       base_path="Atom.Header.Context", allowed_values=("Decision",), form_roles=("Method",))''',
    }
    return native_claims


class CandidateSchemaTests(unittest.TestCase):
    def test_reviewed_atom_dependencies_callback_survives_asset_compilation(self):
        claim = """from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Atom

def dependencies_are_distinct(atom: Atom) -> bool:
    return len(atom.dependencies) == len(set(atom.dependencies))

declare_entity(
    entity_name="Dependencies",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context.Topics",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_format=str,
    value_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_cardinality=0,
    instance_check=dependencies_are_distinct,
)
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'model'
            root.mkdir()
            (root / 'CA-R-1.md').write_text(source('CA-R-1', body='''## Claim
### Formal Claim
```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
class Requirement(Atom):
    pass
declare_entity(entity_name="Requirement", entity_class=Requirement,
               qualification_property_path="Atom.Header.Context.Role")
```
'''))
            target = root / 'CA-R-4001.md'
            subject = 'ANECHOIC_MODEL<+Atom.Header.Context.Topics.Dependencies'
            carrier = source('CA-R-4001', body='## Claim\n### Formal Claim\n```python\n' + claim + '```\n')
            carrier = carrier.replace('version: 1\n', f'version: 1\ntopics:\n  main_subject: {subject}\n')
            target.write_text(carrier)
            asset = root.parent / 'schema.json'
            asset.write_bytes(compile_candidate_schema(root))
            compiled = json.loads(asset.read_bytes())
            self.assertEqual('CA-R-4001', compiled['atom_dependencies_check']['source']['atom_id'])
            self.assertTrue(load_candidate_schema(asset).atom_dependencies_check)

    def test_cli_selects_sources_and_only_formal_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'model'
            root.mkdir()
            encoded = _formal_fixture_source()
            (root / 'CA-R-1.md').write_text(encoded.replace('role: Requirement', 'role: requirement')
                                           .replace('form: Declaration', 'form: declaration'))
            native_claims = _native_claim_fixtures()
            for atom_id, claim in native_claims.items():
                (root / f'{atom_id}.md').write_text(source(atom_id, body=(
                    '## Claim\n### Formal Claim\n```python\nfrom anechoic.formal_claims import declare_entity\n'
                    + claim + '\n```\n'
                )))
            (root / 'CA-R-2.md').write_text(source('CA-R-2', status='Draft', body='invalid'))
            (root / 'archive').mkdir()
            (root / 'archive/CA-R-3.md').write_text('invalid')
            output = Path(directory) / 'output/schema.json'
            subprocess.run([sys.executable, "-B", str(Path(__file__).with_name('legacy_candidate_schema__pub.py')),
                            '--model-root', str(root), '--output', str(output)], check=True)
            asset = json.loads(output.read_text())
            self.assertEqual([(atom_id, 1, f'{atom_id}.md') for atom_id in ('CA-R-1', *native_claims)],
                             [(s['atom_id'], s['version'], s['path']) for s in asset['workbench']['sources']])
            compiled = load_candidate_schema(output)
            self.assertIn('header.identity.atom_id', compiled.header(1).names)
            self.assertEqual(('content.summary',), compiled.content.names)
            rule = compiled.content.rules[0]
            self.assertEqual(('CA-R-1', 1, 'CA-R-1.md'),
                             (rule.source.reference, rule.source.version, rule.source.source_path))
            compiled.validate_role_form('Plan', 'Plan')
            compiled.validate_role_form('Method', 'Decision')
            with self.assertRaisesRegex(ValueError, 'not permitted'):
                compiled.validate_role_form('Plan', 'Decision')
            with self.assertRaisesRegex(ValueError, 'not declared'):
                compiled.validate_role_form('Unknown', 'Decision')
            compiled.validate_role_form('Plan', 'Unclassified')
            self.assertEqual('decision', compiled.role_form.encode('form', 'Decision'))
            self.assertEqual('Decision', compiled.role_form.decode('form', 'decision'))
            self.assertEqual('Unclassified', compiled.role_form.encode('form', 'Unclassified'))
            self.assertNotIn('Phantom', compiled.role_form.roles)
            self.assertEqual(output.read_bytes(), compile_candidate_schema(root))
            asset['role_form'][0]['value'] = 'tampered'
            output.write_text(json.dumps(asset))
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                load_candidate_schema(output)

    def test_sealed_core_declarations_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'schema.json'
            path.write_bytes(compile_candidate_schema(CORE))
            asset = json.loads(path.read_text())
            self.assertTrue(asset['workbench']['sources'])
            compiled = load_candidate_schema(path)
            self.assertTrue(compiled.header(1).names)
            self.assertTrue(compiled.content.rules)
            self.assertIn('IS_WORK_REPORT_FOR', compiled.header_relation_rules['names'])
            self.assertNotIn('BLOCKS', compiled.header_relation_rules['names'])
            self.assertIn(('Plan', 'Plan'), compiled.role_form.qualified)
            compiled.validate_role_form('Plan', 'Plan')
            with self.assertRaisesRegex(ValueError, 'not permitted for Form Plan'):
                compiled.validate_role_form('Method', 'Plan')
            compiled.validate_role_form('Method', 'Decision')
            compiled.validate_role_form('Operations', 'Direct Policy')
            compiled.validate_role_form('Operations', 'Workflow')
            with self.assertRaises(ValueError):
                compiled.validate_role_form('Requirement', 'Decision')
            with self.assertRaises(ValueError):
                compiled.validate_role_form('Method', 'Work Report')
            with self.assertRaises(ValueError):
                compiled.validate_role_form('Plan', 'Workflow')
            self.assertIn(('Requirement', 'Declaration'), compiled.role_form.qualified)
            self.assertIn('Work Report', compiled.role_form.forms)

    def test_codec_rejects_collisions(self):
        schema = RoleFormSchema(frozenset(), frozenset({'Work Report', 'Work-Report'}), frozenset(), ())
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            schema.encode('form', 'Work Report')


if __name__ == '__main__':
    unittest.main()
