from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import read_active_model_sources
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import _NativeModel
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component

ROOT = Path(__file__).resolve().parents[6]
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
                  'tier': 0, 'lens': 'SPEC'}
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
                  'version': 1, 'status': 'active', 'updated_at': datetime.now(timezone.utc), 'lens': 'SPEC'}
        self.assertEqual(model._validate('Axiom', fields, {'IS_CONTAINED_BY': [project]}).tier, 0)
        self.assertEqual(model._validate('Axiom', {**fields, 'tier': 1}, {'IS_CONTAINED_BY': [project]}).tier, 1)

    def test_explicit_c9_scope_and_custom_derived_scope(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
        records = read_active_model_sources(self.root, self.ontology)
        text = 'from anechoic.model import SpecAtom\nclass MyNode(SpecAtom):\n    pass\n'
        explicit = 'MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//My Node'
        self.assertEqual(lower_typed_node(text, records, explicit)[0][0], explicit)
        self.assertTrue(lower_typed_node(text, records)[0][0].endswith('//MyNode'))

    def test_lowering_display_name_and_direct_inherited_property(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
        records = read_active_model_sources(self.root, self.ontology)
        base = 'from anechoic.formal_claims import value\nfrom anechoic.model import Project, SpecAtom\n'
        scope = 'MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Example Node'
        text = base + 'class ExampleNode(SpecAtom):\n    container_type = value(fixed=Project)\n    encapsulation = value(fixed="white_box")\n'
        lowered = lower_typed_node(text, records, scope)
        self.assertIn("entity_name='Example Node Constraints'", lowered[1][1])
        self.assertEqual(lowered[2][0], scope + '.Encapsulation')
