from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import read_active_model_sources
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import _NativeModel
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component

ROOT = Path(__file__).resolve().parents[7]
AXIOM = '''---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3193
structure:
  container:
    component: C00
context:
  template: manifest_node
state:
  status: active
  version: 4
  updated_at: '2026-11-24T15:59:19+00:00'
---
## Formal Manifest

```python anechoic-edsl
from anechoic.formal_claims import value
from anechoic.model import Lens, Project, SpecAtom
class Axiom(SpecAtom):
    tier = value(fixed=0)
    lens = value(fixed=Lens.SPEC)
    container_type = value(fixed=Project)
```
'''


class TypedNodePilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.ontology = self.root / 'LAYER_1_META_ONTOLOGY_C9'
        source = find_ontology_component(ROOT / '_anechoic_anechoic')
        self.assertIsNotNone(source)
        shutil.copytree(source, self.ontology)
        custom = self.root / '__PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        self.source = custom / 'AN-C-3193-MANIFEST_NODE--axiom.md'
        self.source.write_text(AXIOM)

    def model(self):
        return _NativeModel(records=read_active_model_sources(self.root, self.ontology))

    def test_axiom_values_and_container(self):
        model = self.model()
        project = model._validate('Project', {}, {})
        fields = {'atom_family': 'SPEC', 'atom_id': 'AN-S-111', 'container': {'component': 'C00'},
                  'version': 1, 'status': 'active', 'updated_at': datetime.now(timezone.utc),
                  'tier': 0, 'lens': 'SPEC', 'summary': 'Example Axiom'}
        model._validate('Axiom', fields, {'IS_CONTAINED_BY': [project]})
        model._validate('Axiom', {k: v for k, v in fields.items() if k != 'lens'}, {'IS_CONTAINED_BY': [project]})
        for changed in ({**fields, 'tier': 1}, {**fields, 'lens': 'QA'}):
            with self.assertRaises(ValueError):
                model._validate('Axiom', changed, {'IS_CONTAINED_BY': [project]})
        for targets in ([], [project, project]):
            with self.assertRaises(ValueError):
                model._validate('Axiom', fields, {'IS_CONTAINED_BY': targets})
        self.source.write_text(AXIOM.replace('Lens.SPEC', 'Lens.UNKNOWN'))
        with self.assertRaises(ValueError):
            self.model()

    def test_default_is_overrideable(self):
        self.source.write_text(AXIOM.replace('tier = value(fixed=0)', 'tier = value(default=0)'))
        model = self.model()
        project = model._validate('Project', {}, {})
        fields = {'atom_family': 'SPEC', 'atom_id': 'AN-S-111', 'container': {'component': 'C00'},
                  'version': 1, 'status': 'active', 'updated_at': datetime.now(timezone.utc),
                  'lens': 'SPEC', 'summary': 'Example Axiom'}
        self.assertEqual(model._validate('Axiom', fields, {'IS_CONTAINED_BY': [project]}).tier, 0)
        self.assertEqual(model._validate('Axiom', {**fields, 'tier': 1}, {'IS_CONTAINED_BY': [project]}).tier, 1)

    def test_explicit_c9_scope_and_custom_derived_scope(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
        records = read_active_model_sources(self.root, self.ontology)
        text = 'from anechoic.model import SpecAtom\nclass MyNode(SpecAtom):\n    pass\n'
        explicit = 'MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//My Node'
        self.assertEqual(lower_typed_node(text, records, explicit)[0][0], explicit)
        self.assertTrue(lower_typed_node(text, records)[0][0].endswith('//MyNode'))

    def test_lowering_display_name_and_direct_inherited_property(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
        records = read_active_model_sources(self.root, self.ontology)
        base = 'from anechoic.formal_claims import value\nfrom anechoic.model import Project, SpecAtom\n'
        scope = 'MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Example Node'
        text = base + 'class ExampleNode(SpecAtom):\n    container_type = value(fixed=Project)\n    encapsulation = value(fixed="white_box")\n'
        lowered = lower_typed_node(text, records, scope)
        self.assertIn("entity_name='Example Node Constraints'", lowered[1][1])
        self.assertEqual(lowered[2][0], scope + '.Encapsulation')


def test_ssot_carrier_fixed_class_and_validation():
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
    def record(name, base, path):
        imports = f'from anechoic.model import {base}\n' if base else ''
        signature = f'({base})' if base else ''
        return ('source', 'MODEL//ANECHOIC <+ ' + path,
                f'from anechoic.formal_claims import declare_entity\n{imports}class {name}{signature}:\n    pass\ndeclare_entity(entity_name={name!r}, entity_class={name})\n')
    records = [record('Node', '', 'Node'), record('Carrier', '', 'Carrier'),
               record('Markdown', 'Carrier', 'Carrier//Markdown')]
    prefix = 'from anechoic.formal_claims import value\nfrom anechoic.model import Node, Carrier, Markdown\nclass Example(Node):\n    node.ssot_carrier = value('
    for name, path in [('Carrier', 'Carrier'), ('Markdown', 'Carrier//Markdown')]:
        claim = lower_typed_node(prefix + f'fixed={name})\n', records)[0][1]
        assert parse_native_model_claim(claim)['arguments']['ssot_carrier_path'] == path
    for expression in ('default=Markdown', 'fixed=Node', 'fixed="Markdown"'):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'ssot_carrier requires'):
            lower_typed_node(prefix + expression + ')\n', records)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'unknown ssot_carrier'):
        lower_typed_node(prefix + 'fixed=Markdown)\n', records[:2])
    eligibility = 'from anechoic.formal_claims import value\nfrom anechoic.model import Node\nclass Example(Node):\n    node.creation_enabled = '
    for expression in ('value(default=False)', "value(fixed='false')"):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'fixed boolean'):
            lower_typed_node(eligibility + expression + '\n', records)


def test_ticket_subtype_template_uses_inherited_property():
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim

    records = [
        ('atom', 'MODEL//ANECHOIC <+ Atom', "from anechoic.formal_claims import declare_entity\nclass Atom:\n    pass\ndeclare_entity(entity_name='Atom', entity_class=Atom)\n"),
        ('ticket', 'MODEL//ANECHOIC <+ Atom//Ticket', "from anechoic.formal_claims import declare_entity\nfrom anechoic.model import Atom\nclass TicketAtom(Atom):\n    pass\ndeclare_entity(entity_name='Ticket', entity_class=TicketAtom)\n"),
        ('property', 'MODEL//ANECHOIC <+ Atom.Header.Context.Template', "from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Template', entity_kind='Property', relation_name='IS_PROPERTY_OF', base_path='Atom.Header.Context', value_format=str, field_options={'default': None, 'kw_only': True})\n"),
        ('fallback', 'MODEL//ANECHOIC <+ Atom.Header.Context.Template fallback', "from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Template', entity_kind='Property', relation_name='IS_PROPERTY_OF', base_path='Atom.Header.Context', value_format=str, applies_to_entity_classes=('Atom//Ticket',), fallback_property_name='Form')\n"),
    ]
    before = records.copy()
    for name, value in (('Task', 'task'), ('WorkReport', 'work_report')):
        text = ('from anechoic.formal_claims import value\nfrom anechoic.model import TicketAtom\n'
                f'class {name}(TicketAtom):\n    node.template = value(fixed={value!r})\n')
        lowered = lower_typed_node(text, records)
        args = parse_native_model_claim(lowered[1][1])['arguments']
        assert args['allowed_values'] == (value,)
        assert args['applies_to_entity_classes'] == (f'Atom//Ticket//{name}',)
        assert args['base_path'] == 'Atom.Header.Context'
    assert records == before
    assert parse_native_model_claim(records[-1][2])['arguments']['fallback_property_name'] == 'Form'


def test_node_marker_is_static_and_lowers_to_a_class():
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_typed_manifest_node
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import _validate_c9_typed_manifest
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError

    record = ('source', 'MODEL//ANECHOIC <+ Node',
              "from anechoic.formal_claims import declare_entity\nclass Node:\n    pass\ndeclare_entity(entity_name='Node', entity_class=Node)\n")
    assert parse_typed_manifest_node('node(Root)')['bases'] == ()
    claim = lower_typed_node('node(Example, Node)', [record])[0][1]
    assert 'from anechoic.model import Node\nclass Example(Node):\n    pass' in claim
    header = {'atom_family': 'SPEC', 'atom_id': 'AN-S-100', 'container': {'component': 'C9'}, 'tier': 2,
              'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-11-24T00:00:00Z'},
              'context': {'lens': 'DOM/CONT', 'template': 'manifest_node'},
              'concern': {'subject': 'Example', 'path': 'Model/Graph/Node', 'relation': 'is_narrower_than'}}
    body = '## Formal Manifest\n\n```python anechoic-edsl\n{}\n```\n'
    _validate_c9_typed_manifest(header, body.format('node(Example, Node)'))
    for invalid in ('node()', 'node("Example")', 'node(Example, Node, Node)',
                    'node(Example, Property)', 'node(Example, base=Node)',
                    'node(Example)\nprint(1)', 'node(Example, dangerous())'):
        with unittest.TestCase().assertRaises(ValueError):
            parse_typed_manifest_node(invalid)
        with unittest.TestCase().assertRaises(InputError):
            _validate_c9_typed_manifest(header, body.format(invalid))
    for template in ('manifest_property', 'manifest_relation'):
        with unittest.TestCase().assertRaises(InputError):
            _validate_c9_typed_manifest({**header, 'context': {'lens': 'DOM/CONT', 'template': template}},
                                        body.format('node(Example, Node)'))


def test_node_parts_and_alternatives_are_static_and_checked():
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import _collect_node_metadata
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_typed_manifest_node

    def record(name, path):
        return ('source', 'MODEL//ANECHOIC <+ ' + path,
                f"from anechoic.formal_claims import declare_entity\nclass {name}:\n    pass\ndeclare_entity(entity_name={path.rsplit('/', 1)[-1]!r}, entity_class={name}, entity_kind='Primary')\n")
    records = [record('Root', 'Root'), record('Child', 'Root//Child'), record('Other', 'Other')]
    source = ("from anechoic.model import Child, Other\nclass Root:\n"
              "    node.parts = {'CH': Child, '=>OT': Other}\n"
              "    node.alternatives = (('CH',), ('=>OT',))\n")
    addresses = {'Root': 'Root', 'Child': 'Root//Child', 'Other': 'Other'}
    locations = {'MODEL//ANECHOIC <+ Root//Child': ('Root', '/', 'Child')}
    output = {}
    _collect_node_metadata(records, [('source', 'MODEL//ANECHOIC <+ Root', source, 'manifest_node')],
                           addresses, locations, output)
    assert output == {'node_parts': {'MODEL//ANECHOIC <+ Root': [['CH', 'Root//Child'], ['=>OT', 'Other']]},
                      'node_alternatives': {'MODEL//ANECHOIC <+ Root': [['CH'], ['=>OT']]},
                      'node_aliases': {}}
    for invalid in (source.replace("'=>OT': Other", "'OT': Other"),
                    source.replace("('=>OT',)", "('missing',)"),
                    source.replace("'=>OT': Other", "'=>OT': Child, '=>OT': Other"),
                    source.replace("'=>OT': Other", "'CH2': Child, '=>OT': Other"),
                    source.replace("'=>OT': Other", "'=>OT': Missing"),
                    source.replace("('=>OT',)", "('CH',)")):
        with unittest.TestCase().assertRaises(ValueError):
            _collect_node_metadata(records, [('source', 'MODEL//ANECHOIC <+ Root', invalid, 'manifest_node')],
                                   addresses, locations, {})
    with unittest.TestCase().assertRaises(ValueError):
        parse_typed_manifest_node(source.replace("'=>OT': Other", "'=>OT': Missing"))


def test_node_aliases_are_static_and_unique_among_admitted_siblings():
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import _collect_node_metadata
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_typed_manifest_node

    def record(name):
        return ('source', 'MODEL//ANECHOIC <+ Root//' + name,
                f"from anechoic.formal_claims import declare_entity\nclass {name}:\n    pass\ndeclare_entity(entity_name={name!r}, entity_class={name}, entity_kind='Primary')\n")
    records = [record('First'), record('Second')]
    addresses = {name: 'Root//' + name for name in ('First', 'Second')}
    locations = {subject: ('Root', '//', subject.rsplit('/', 1)[-1]) for _, subject, _ in records}
    def source(name, aliases):
        return f'class {name}:\n    node.aliases = {aliases}\n'
    first = source('First', "('Alternate', 'Another')")
    typed = [('first', records[0][1], first, 'manifest_node')]
    output = {}
    _collect_node_metadata(records, typed, addresses, locations, output)
    assert output['node_aliases'] == {records[0][1]: ['Alternate', 'Another']}
    for invalid in ("()", "('',)", "(' A',)", "('A/B',)", "('=>A',)", "('A', 'A')", "(A,)"):
        with unittest.TestCase().assertRaises(ValueError):
            parse_typed_manifest_node(source('First', invalid))
    for name in ('First', 'Second'):
        with unittest.TestCase().assertRaises(ValueError):
            _collect_node_metadata(records, [('first', records[0][1], source('First', repr((name,))), 'manifest_node')],
                                   addresses, locations, {})
    with unittest.TestCase().assertRaises(ValueError):
        _collect_node_metadata(records, typed + [('second', records[1][1], source('Second', "('Alternate',)"), 'manifest_node')],
                               addresses, locations, {})
    with unittest.TestCase().assertRaises(ValueError):
        _collect_node_metadata(records, typed, addresses, {}, {})
