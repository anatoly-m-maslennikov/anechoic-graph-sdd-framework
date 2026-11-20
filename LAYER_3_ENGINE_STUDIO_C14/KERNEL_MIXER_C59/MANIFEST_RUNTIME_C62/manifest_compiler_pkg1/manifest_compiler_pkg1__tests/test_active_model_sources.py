from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[5]
PROGRAMMATIC = ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC'
sys.path[:0] = [str(ROOT), str(PROGRAMMATIC), str(PROGRAMMATIC / 'FEATURE_TOOLS'), str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'IWE_CONSOLE_C43')]
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1 import active_model_sources as sources  # noqa: E402

CLAIM = "from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Atom')\n"


def carrier(identifier='AN-S-1', subject='MODEL//ANECHOIC <+ Atom', status='active', version=1):
    return (f'---\nidentity:\n  atom_id: {identifier}\ncontext:\n  container:\n    component: C9\n'
            f'  lens: SPEC\nstate:\n  status: {status}\n  version: {version}\n---\n'
            f'## Claim scope\n\n{subject}\n\n## Claim\n\n### Formal Claim\n\n```python\n{CLAIM}```\n')


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
        return sources.read_active_model_sources(self.root, self.component)

    def test_selection_and_out_of_scope(self):
        self.put('AN-S-1-SPEC--atom.md', carrier(version=2))
        self.put('AN-S-2-SPEC--draft.md', carrier('AN-S-2', status='draft'))
        self.put('AN-S-3-SPEC--other.md', carrier('AN-S-3', subject='Other'))
        (self.component / '000_draft').mkdir()
        (self.component / '000_draft' / 'bad.md').write_text('bad')
        self.assertEqual(self.read(), (('META_ONTOLOGY_C9/AN-S-1-SPEC--atom.md@2', 'MODEL//ANECHOIC <+ Atom', CLAIM),))

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

    def test_changed_input_rejected(self):
        self.put('AN-S-1-SPEC--atom.md', carrier())
        with patch.object(sources.ReadContext, 'currentness', return_value={'state': 'changed'}):
            with self.assertRaisesRegex(ValueError, 'changed'):
                self.read()



if __name__ == '__main__':
    unittest.main()
