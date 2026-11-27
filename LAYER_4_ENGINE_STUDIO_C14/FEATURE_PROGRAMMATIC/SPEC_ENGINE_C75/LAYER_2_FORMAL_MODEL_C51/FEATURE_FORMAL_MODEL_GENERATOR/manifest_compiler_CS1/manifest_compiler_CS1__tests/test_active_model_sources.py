from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[7]
PROGRAMMATIC = ROOT / 'LAYER_4_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC'
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import read_active_model_sources  # noqa: E402
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import active_model_sources as sources  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext  # noqa: E402

CLAIM = "from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Atom')\n"


def carrier(identifier='AN-S-1', subject='MODEL//ANECHOIC <+ Atom', status='active', version=1):
    return (f'---\nidentity:\n  atom_id: {identifier}\ncontext:\n  container:\n    component: C9\n'
            f'  lens: SPEC\nstate:\n  status: {status}\n  version: {version}\n---\n'
            f'## Claim scope\n\n{subject}\n\n## Claim\n\n### Formal Claim\n\n```python\n{CLAIM}```\n')


def custom_carrier(identifier='AN-C-1', subject='MODEL//ANECHOIC <+ Node', status='active'):
    return (f'---\natom_family: PROJECT_CONFIG\natom_id: {identifier}\nstructure:\n  container:\n    component: C00\n'
            f'context:\n  template: model_manifest\nstate:\n  status: {status}\n  version: 1\n'
            f'  updated_at: 2026-11-20T00:00:00Z\n---\n'
            f'## Semantics\n\nSemantics.\n\n## Formal Manifest\n\n### Node\n\n{subject}\n\n```python\n{CLAIM}```\n')


class ActiveModelSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.component = self.root / 'META_ONTOLOGY_C9'
        self.component.mkdir()

    def put(self, filename, text):
        (self.component / filename).write_text(text)

    def read(self):
        return read_active_model_sources(self.root, self.component)

    def test_selection_and_out_of_scope(self):
        self.put('AN-S-1-SPEC--atom.md', carrier(version=2))
        self.put('AN-S-2-SPEC--draft.md', carrier('AN-S-2', status='draft'))
        self.put('AN-S-3-SPEC--other.md', carrier('AN-S-3', subject='Other'))
        (self.component / '000_draft').mkdir()
        (self.component / '000_draft' / 'bad.md').write_text('bad')
        self.assertEqual(self.read(), (('META_ONTOLOGY_C9/AN-S-1-SPEC--atom.md@2', 'MODEL//ANECHOIC <+ Atom', CLAIM),))

    def test_typed_des_property_selected_and_legacy_des_excluded(self):
        folder = self.component / '_DES'
        folder.mkdir()
        typed = (carrier('AN-S-2', subject='MODEL//ANECHOIC <+ Atom.Content')
                 .replace('  lens: SPEC', '  lens: DES\n  template: manifest_property')
                 .replace('## Claim\n\n### Formal Claim\n\n```python\n' + CLAIM,
                          '## Formal Manifest\n\n```python anechoic-edsl\n'
                          'from anechoic.model import Atom, Property\n'
                          'class Content(Property):\n    bearer = Atom\n    value_cardinality = 0\n'))
        (folder / 'AN-S-2-SPEC--content.md').write_text(typed)
        (folder / 'AN-S-3-SPEC--legacy.md').write_text(carrier('AN-S-3').replace('lens: SPEC', 'lens: DES'))
        with patch.object(sources, '_lower_active_sources', side_effect=lambda records, subjects, typed, **kw: (records, typed)):
            records, selected = self.read()
        self.assertEqual([], records)
        self.assertEqual(1, len(selected))
        self.assertIn('/_DES/AN-S-2-', selected[0][0])
        self.assertEqual('manifest_property', selected[0][3])

    def test_spec_directory_and_cross_layout_duplicate(self):
        spec = self.component / '_SPEC'
        spec.mkdir()
        (spec / 'AN-S-1-SPEC--atom.md').write_text(carrier())
        self.assertEqual(self.read()[0][0], 'META_ONTOLOGY_C9/_SPEC/AN-S-1-SPEC--atom.md@1')
        self.put('AN-S-1-SPEC--other.md', carrier(subject='MODEL//ANECHOIC <+ Node'))
        with self.assertRaisesRegex(ValueError, 'duplicate Model source ID'):
            self.read()

    def test_new_custom_config_directory(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        custom = self.root / '__PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        (custom / 'AN-C-1-MODEL_MANIFEST--node.md').write_text(custom_carrier())
        self.assertEqual(len(self.read()), 2)

    def test_raw_custom_node_axis_values_are_checked(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_property_relation_lowering import lower_typed_fields

        scope = 'MODEL//ANECHOIC <+ Graph/Axis >| Temporality'
        axis = ("from anechoic.model import Property, Axis\n"
                "class Temporality(Property):\n    bearer = Axis\n"
                "    property.axis = True\n    allowed_values = ('Continuant',)\n")
        claim = lower_typed_fields('manifest_property', axis, scope, {'Axis': 'Graph/Axis'})
        self.put('AN-S-1-SPEC--axis.md', carrier(subject=scope).replace(CLAIM, claim + '\n'))
        custom = self.root / '__PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        path = custom / 'AN-C-1-MODEL_MANIFEST--node.md'
        node = ("from anechoic.formal_claims import declare_entity\n"
                "from anechoic.model import Node\n"
                "class Probe(Node):\n    pass\n"
                "declare_entity(entity_name='Probe', entity_class=Probe, "
                "entity_kind='Primary', axes={'Temporality': 'Continuant'})\n")
        path.write_text(custom_carrier(subject='MODEL//ANECHOIC <+ Probe').replace(CLAIM, node))
        with patch.object(sources, '_check_relation_references'):
            self.assertEqual(len(self.read()), 2)
            path.write_text(path.read_text().replace('Continuant', 'Bogus'))
            with self.assertRaisesRegex(ValueError, 'unadmitted Entity axis Temporality=Bogus'):
                self.read()

    def test_canonical_header_classifies_model(self):
        text = carrier().replace('identity:\n  atom_id: AN-S-1', 'atom_family: SPEC\natom_id: AN-S-1')
        text = text.replace('context:\n  container:', 'structure:\n  tier: 1\n  container:')
        text = text.replace('  lens: SPEC', 'context:\n  lens: SPEC')
        text = text.replace('  version: 1', '  version: 1\n  updated_at: 2026-11-20T00:00:00Z')
        self.put('AN-S-1-OTHER--atom.md', text)
        self.assertEqual(1, len(self.read()))

    def test_duplicate_id_subject_and_invalid(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        for name, text in [
            ('AN-S-1-SPEC--duplicate.md', carrier(subject='MODEL//ANECHOIC <+ Node')),
            ('AN-S-2-SPEC--duplicate.md', carrier('AN-S-2')),
            ('AN-S-2-SPEC--invalid.md', carrier('AN-S-2', subject='MODEL//ANECHOIC <+')),
            ('wrong.md', carrier('AN-S-2', subject='MODEL//ANECHOIC <+ Node')),
        ]:
            with self.subTest(name=name):
                self.put(name, text)
                with self.assertRaises(ValueError):
                    self.read()
                (self.component / name).unlink()

    def test_custom_sources_are_shallow_and_share_duplicate_checks(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        custom = self.root / '002_PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        declaration = custom / 'AN-C-1-MODEL_MANIFEST--node.md'
        declaration.write_text(custom_carrier())
        (custom / 'AN-C-2-MODEL_MANIFEST--draft.md').write_text(custom_carrier('AN-C-2', status='draft'))
        (custom / '099_archived').mkdir()
        (custom / '099_archived' / 'bad.md').write_text('bad')
        self.assertEqual(len(self.read()), 2)
        declaration.write_text(custom_carrier(subject='MODEL//ANECHOIC <+ Atom'))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.read()

    def test_custom_source_requires_native_identity_and_model_scope(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        custom = self.root / '002_PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        declaration = custom / 'AN-C-1-MODEL_MANIFEST--node.md'
        declaration.write_text(custom_carrier(subject='Other'))
        with self.assertRaisesRegex(ValueError, 'Model Claim scope'):
            self.read()
        declaration.write_text(custom_carrier('AN-P-1'))
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.read()

    def test_custom_multiple_declarations_and_rejections(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        custom = self.root / '002_PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        declaration = custom / 'AN-C-1-MODEL_MANIFEST--node.md'
        text = custom_carrier() + f'\n### Other\n\nMODEL//ANECHOIC <+ Other\n\n```python\n{CLAIM}```\n'
        declaration.write_text(text)
        self.assertEqual(len(self.read()), 3)
        for invalid in (
            text.replace('MODEL//ANECHOIC <+ Other', 'MODEL//ANECHOIC <+ Node'),
            text.replace('MODEL//ANECHOIC <+ Other', 'Other'),
            text + '\n#### Nested\n\nignored\n',
            text + '\nExtra text\n',
            text.replace("declare_entity(entity_name='Atom')", "declare_entity(entity_name='Atom')\nprint('unsafe')"),
        ):
            with self.subTest(invalid=invalid[-60:]):
                declaration.write_text(invalid)
                with self.assertRaises(ValueError):
                    self.read()
        declaration.write_text(custom_carrier())
        (custom / 'AN-C-1-MODEL_MANIFEST--duplicate.md').write_text(custom_carrier(subject='MODEL//ANECHOIC <+ Other'))
        with self.assertRaisesRegex(ValueError, 'duplicate Model source ID'):
            self.read()

    def test_typed_template_must_match_class(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        custom = self.root / '__PROJECT_CONFIG' / 'CUSTOM_MODEL'
        custom.mkdir(parents=True)
        typed = custom_carrier().replace('template: model_manifest', 'template: manifest_node')
        typed = typed.replace('### Node\n\nMODEL//ANECHOIC <+ Node\n\n```python\n' + CLAIM,
                              '```python anechoic-edsl\nfrom anechoic.model import Property\nclass Example(Property):\n    pass\n')
        (custom / 'AN-C-1-MANIFEST_NODE--node.md').write_text(typed)
        with self.assertRaisesRegex(ValueError, 'template and class do not match'):
            self.read()

    def test_c9_typed_template_mismatch_rejected_for_all_kinds(self):
        for template, base in (('manifest_node', 'Property'), ('manifest_property', 'Relation'),
                               ('manifest_relation', 'NodeConstraints')):
            text = carrier().replace('  lens: SPEC', f'  lens: SPEC\n  template: {template}')
            text = text[:text.index('## Claim\n')] + f'## Formal Manifest\n\n```python anechoic-edsl\nfrom anechoic.model import {base}\nclass Example({base}):\n    pass\n```\n'
            self.put('AN-S-1-SPEC--atom.md', text)
            with self.subTest(template=template), self.assertRaisesRegex(ValueError, 'template and class do not match'):
                self.read()

    def test_typed_c9_without_scope_is_rejected(self):
        text = carrier().replace('  lens: SPEC', '  lens: SPEC\n  template: manifest_node')
        text = text.replace('MODEL//ANECHOIC <+ Atom', 'Other')
        self.put('AN-S-1-SPEC--atom.md', text)
        with self.assertRaisesRegex(ValueError, 'typed Manifest requires a Model Claim scope'):
            self.read()

    def test_unscoped_c9_property_matches_scoped_property(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import _validate_c9_typed_manifest

        atom = CLAIM.replace("declare_entity(entity_name='Atom')",
                             "class Atom:\n    pass\ndeclare_entity(entity_name='Atom', entity_class=Atom, entity_kind='Primary')")
        self.put('AN-S-1-SPEC--atom.md', carrier().replace(CLAIM, atom))
        scope = 'MODEL//ANECHOIC <+ Atom.Header.Relations'
        relations = (carrier('AN-S-2', subject=scope)
                     .replace('  lens: SPEC', '  lens: SPEC\n  template: manifest_property')
                     .replace('## Claim\n\n### Formal Claim\n\n```python\n' + CLAIM,
                              '## Formal Manifest\n\n```python anechoic-edsl\n'
                              'from anechoic.model import Atom, Property\n'
                              "class AtomRelations(Property):\n    name = 'Relations'\n"
                              '    bearer = Atom.Header\n    value_cardinality = 0\n'))
        header_scope = 'MODEL//ANECHOIC <+ Atom.Header'
        header = (relations.replace('AN-S-2', 'AN-S-3').replace(scope, header_scope)
                  .replace('AtomRelations', 'Header').replace("'Relations'", "'Header'")
                  .replace('bearer = Atom.Header', 'bearer = Atom'))
        self.put('AN-S-2-SPEC--relations.md', relations)
        self.put('AN-S-3-SPEC--header.md', header)
        relation = ("from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='IS_PROPERTY_OF', "
                    "source_endpoint={'level': 'model_entities'}, target_endpoint={'level': 'model_entities'})\n")
        self.put('AN-S-4-SPEC--is-property-of.md', carrier(
            'AN-S-4', subject='MODEL//ANECHOIC <+ Graph/Relation//IS_PROPERTY_OF').replace(CLAIM, relation))
        scoped = self.read()
        self.assertEqual(scoped[2][:2], ('META_ONTOLOGY_C9/AN-S-2-SPEC--relations.md@1', scope))

        def unscoped(text, subject):
            return text.replace(f'## Claim scope\n\n{subject}\n\n', '')

        self.put('AN-S-2-SPEC--relations.md', unscoped(relations, scope))
        self.put('AN-S-3-SPEC--header.md', unscoped(header, header_scope))
        rows = []
        for path in sorted(self.component.glob('*.md')):
            source = path.relative_to(self.root).as_posix()
            parsed = sources.parse_carrier(path.read_bytes(), path)
            rows.append(dict(source_path=source, exact_ref=f"{parsed.metadata['identity']['atom_id']}@1",
                             metadata=parsed.metadata, body=parsed.body))
        _validate_c9_typed_manifest(rows[1]['metadata'], rows[1]['body'])
        self.assertEqual(self.read(), scoped)
        self.assertEqual(sources.compile_active_model_rows(rows, has_c9=True), scoped)
        rows[1]['body'] = rows[1]['body'].replace('    bearer = Atom.Header\n',
                                                  '    bearer = Atom.Header\n    classification = True\n')
        with self.assertRaisesRegex(ValueError, 'Invalid typed Model scope'):
            _validate_c9_typed_manifest(rows[1]['metadata'], rows[1]['body'])
        with self.assertRaisesRegex(ValueError, 'ordinary Property'):
            sources.compile_active_model_rows(rows, has_c9=True)

    def test_changed_input_rejected(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        with patch.object(ReadContext, 'currentness', return_value={'state': 'changed'}):
            with self.assertRaisesRegex(ValueError, 'changed'):
                self.read()



if __name__ == '__main__':
    unittest.main()


def test_continuant_disk_and_row_compilation(tmp_path):
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import compile_active_model_rows
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier

    root = tmp_path.resolve()
    folder = root / 'META_ONTOLOGY_C9' / '_DOM' / 'CONT'
    folder.mkdir(parents=True)
    text = '''---
atom_family: SPEC
atom_id: AN-S-1
concern:
  subject: Graph
  path: Model
  relation: is_contained_by
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DOM/CONT
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: 2026-11-20T00:00:00Z
---
## Formal Manifest

```python anechoic-edsl
class Graph:
    pass
```
'''
    path = folder / 'AN-S-1-DOM--graph.md'
    path.write_text(text)
    disk = read_active_model_sources(root, root / 'META_ONTOLOGY_C9')
    carrier = parse_carrier(text.encode(), path)
    rows = [{'source_path': str(path.relative_to(root)), 'exact_ref': 'AN-S-1@1',
             'metadata': carrier.metadata, 'body': carrier.body}]
    assert disk == compile_active_model_rows(rows, has_c9=True)
    assert disk[0][1] == 'MODEL//ANECHOIC <+ Graph'
    for change in (text.replace('  template: manifest_node\n', ''),
                   text.replace('  template: manifest_node', '  template: model_manifest'),
                   text.replace('  path: Model', '  path: Other'),
                   text.replace('  relation: is_contained_by', '  relation: unknown'),
                   text.replace('## Formal Manifest', '## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n\n## Formal Manifest')):
        path.write_text(change)
        with unittest.TestCase().assertRaises(ValueError):
            read_active_model_sources(root, root / 'META_ONTOLOGY_C9')


def test_continuant_node_concern_matches_direct_base():
    check = sources._check_continuant_address
    source = 'META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--task.md@1'
    text = 'class SessionTask(Ephemeral):\n    pass\n'
    addresses = {'Ephemeral': 'Graph/Node//Ephemeral',
                 'OperativePlan': 'Graph/Node//Ephemeral//Operative Plan'}
    check(source, 'MODEL//ANECHOIC <+ Graph/Node//Ephemeral//Session Task',
          text, 'manifest_node', addresses)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'direct node base'):
        check(source, 'MODEL//ANECHOIC <+ Graph/Node//Ephemeral//Operative Plan//Session Task',
              text, 'manifest_node', addresses)
    # Containment is not a claim about inheritance.
    check(source, 'MODEL//ANECHOIC <+ Graph/Node//Ephemeral/Session Task',
          text, 'manifest_node', addresses)


def test_continuant_field_concern_matches_formal_address():
    check = sources._check_continuant_address
    source = 'META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--field.md@1'
    prop = ("from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Tier', entity_kind='Property', "
            "relation_name='IS_PROPERTY_OF', base_path='Graph/Node//Spec.Header', "
            "value_format=int, applies_to_entity_classes=('Graph/Node//Project',))\n")
    text = 'class Tier(Property):\n    pass\n'
    check(source, 'MODEL//ANECHOIC <+ Graph/Node//Project.Header.Tier',
          text, 'manifest_property', {}, prop)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'does not match'):
        check(source, 'MODEL//ANECHOIC <+ Graph/Node//Project.Header.Other',
              text, 'manifest_property', {}, prop)
    relation = ("from anechoic.formal_claims import declare_relation\n"
                "declare_relation(relation_name='CALLS', "
                "source_endpoint={'level': 'model_entities'}, "
                "target_endpoint={'level': 'model_entities'})\n")
    text = 'class Calls(Relation):\n    pass\n'
    check(source, 'MODEL//ANECHOIC <+ Graph/Relation//CALLS', text,
          'manifest_relation', {'Relation': 'Graph/Relation'}, relation)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'does not match'):
        check(source, 'MODEL//ANECHOIC <+ Graph/Relation//OTHER', text,
              'manifest_relation', {'Relation': 'Graph/Relation'}, relation)


def test_continuant_parent_validation_runs_on_ingested_rows(tmp_path):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier

    folder = tmp_path / 'META_ONTOLOGY_C9' / '_DOM' / 'CONT'
    folder.mkdir(parents=True)
    rows = []
    for ident, subject, parent, relation, body in (
        (1, 'Graph', 'Model', 'is_contained_by', 'class Graph:\n    pass'),
        (2, 'Parent', 'Model/Graph', 'is_narrower_than',
         'from anechoic.model import Graph\nclass Parent(Graph):\n    pass'),
        (3, 'Child', 'Model/Graph//Parent', 'is_narrower_than',
         'from anechoic.model import Graph\nclass Child(Graph):\n    pass'),
    ):
        text = f'''---
atom_family: SPEC
atom_id: AN-S-{ident}
concern:
  subject: {subject}
  path: {parent}
  relation: {relation}
container:
  component: C9
tier: 2
context:
  lens: DOM/CONT
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: 2026-11-20T00:00:00Z
---
## Formal Manifest

```python anechoic-edsl
{body}
```
'''
        path = folder / f'AN-S-{ident}-CONT--node.md'
        carrier = parse_carrier(text.encode(), path)
        rows.append({'source_path': str(path.relative_to(tmp_path)),
                     'exact_ref': f'AN-S-{ident}@1', 'metadata': carrier.metadata,
                     'body': carrier.body})
    with unittest.TestCase().assertRaisesRegex(ValueError, 'direct node base'):
        sources.compile_active_model_rows(rows, has_c9=True)


def test_continuant_containment_requires_explicit_pair():
    relation = ("from anechoic.formal_claims import declare_relation\n"
                "declare_relation(relation_name='IS_CONTAINED_BY', endpoint_pairs=("
                "{'source_endpoint': {'level': 'model_entities', 'entity_paths': ('Graph/Node',)}, "
                "'target_endpoint': {'level': 'model_entities', 'entity_paths': ('Graph',)}},))\n")
    records = [('relation', 'MODEL//ANECHOIC <+ Graph/Relation//IS_CONTAINED_BY', relation)]
    source = 'META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--node.md@1'
    def node(scope):
        return (source, 'MODEL//ANECHOIC <+ ' + scope, 'class Node:\n    pass\n', 'manifest_node')
    sources._check_continuant_containment(records, [node('Graph/Node'), node('Model')])
    sources._check_continuant_containment([], [node('Graph/Other')])
    with unittest.TestCase().assertRaisesRegex(ValueError, 'absent from IS_CONTAINED_BY'):
        sources._check_continuant_containment(records, [node('Graph/Other')])


def test_implicit_continuant_node_and_custom_concern():
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import _validate_c9_typed_manifest
    header = {'atom_family': 'SPEC', 'atom_id': 'AN-S-1', 'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-11-24T00:00:00Z'}, 'concern': {'subject': 'Graph', 'path': 'Model',
              'relation': 'is_contained_by'}, 'structure': {'container': {'component': 'C9'}},
              'context': {'lens': 'DOM/CONT', 'template': 'manifest_node'}}
    _validate_c9_typed_manifest(header, '## Summary\n\nGraph\n')
    typed = []
    sources._collect_manifest_claims('## Summary\n\nGraph\n', False, 'node@1',
        'MODEL//ANECHOIC <+ Graph', header['context'], set(), [], typed, header['concern'])
    assert typed[0][2] == 'class Graph:\n    pass\n'
    for subject, relation in [('Graph Node', 'is_contained_by'), ('Graph', 'is_narrower_than')]:
        invalid = {**header, 'concern': {**header['concern'], 'subject': subject, 'relation': relation}}
        with unittest.TestCase().assertRaises(Exception):
            _validate_c9_typed_manifest(invalid, '## Summary\n\nGraph\n')

    metadata = {'atom_family': 'PROJECT_CONFIG', 'atom_id': 'AN-C-1',
        'structure': {'container': {'component': 'C00'}},
        'context': {'template': 'manifest_relation'}, 'state': {'status': 'active', 'version': 1, 'updated_at': '2026-11-24T00:00:00Z'},
        'concern': {'subject': 'APPLIES', 'path': 'Model/Graph/Relation', 'relation': 'is_narrower_than'}}
    body = '## Formal Manifest\n\n```python anechoic-edsl\nclass APPLIES(Relation):\n    pass\n```\n'
    typed = []
    sources._collect_active_source(Path('/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-test.md'),
        True, metadata, body, Path('/snapshot'), set(), set(), [], typed)
    assert typed[0][1] == 'MODEL//ANECHOIC <+ Graph/Relation//APPLIES'
    with unittest.TestCase().assertRaisesRegex(ValueError, 'cannot contain Claim scope'):
        sources._collect_active_source(Path('/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-test.md'),
            True, metadata, '## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n\n' + body,
            Path('/snapshot'), set(), set(), [], [])


def test_split_variant_concern_agrees_with_fixed_template():
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import _validate_c9_typed_manifest

    metadata = {'atom_family': 'PROJECT_CONFIG', 'atom_id': 'AN-C-2',
                'structure': {'container': {'component': 'C00'}},
                'context': {'template': 'manifest_node'},
                'state': {'status': 'active', 'version': 1, 'updated_at': '2026-11-24T00:00:00Z'},
                'concern': {'path': 'Model/Graph/Node//Atom//Spec Atom//.Header.Context',
                            'relation': '.', 'subject': 'Template := axiom'}}
    body = """## Formal Manifest

```python anechoic-edsl
from anechoic.formal_claims import value
from anechoic.model import SpecAtom

class Axiom(SpecAtom):
    node.template = value(fixed='axiom')
```
"""
    path = Path('/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-2-test.md')
    typed = []
    sources._collect_active_source(path, True, metadata, body, Path('/snapshot'), set(), set(), [], typed)
    assert typed[0][1] == 'MODEL//ANECHOIC <+ Graph/Node//Atom//Spec Atom//Axiom'
    draft = {**metadata, 'atom_family': 'SPEC', 'atom_id': 'AN-S-2', 'tier': 2,
             'container': {'component': 'C9'},
             'context': {**metadata['context'], 'lens': 'DOM/CONT'}}
    draft.pop('structure')
    _validate_c9_typed_manifest(draft, body)
    for rule in ("value(fixed='other')", "value(default='axiom')"):
        mismatched = body.replace("value(fixed='axiom')", rule)
        with unittest.TestCase().assertRaisesRegex(ValueError, 'must match the fixed node.template'):
            sources._collect_active_source(path, True, metadata, mismatched,
                Path('/snapshot'), set(), set(), [], [])
        with unittest.TestCase().assertRaises(InputError):
            _validate_c9_typed_manifest(draft, mismatched)
