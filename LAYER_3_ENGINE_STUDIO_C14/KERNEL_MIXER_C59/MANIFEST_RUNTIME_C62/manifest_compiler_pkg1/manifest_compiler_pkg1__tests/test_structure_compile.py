import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC'),
                str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS')]
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1 import structure_compile as compiler  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import parse_structure  # noqa: E402
from native_carrier_header import canonical_native_header, native_header_view  # noqa: E402
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier  # noqa: E402

CONTROL = ROOT / '.anechoic_anechoic'
if (ROOT.parent / 'native-control').is_dir():
    CONTROL = ROOT.parent / 'native-control'
PROJECT = CONTROL / 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
COMPONENT = CONTROL / 'AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md'


def selection(control):
    project = control / PROJECT.name
    raw = project.read_bytes()
    meta = native_header_view(parse_carrier(raw, project).metadata)
    ref = f"{meta['identity']['atom_id']}@{meta['state']['version']}"
    return SimpleNamespace(control_root=control, manifest_path=project, manifest_ref=ref,
                           manifest_sha256=hashlib.sha256(raw).hexdigest())


class Model:
    fingerprint = 'model-fingerprint'
    requires_atom_state = False

    def validate_component_manifest(self, fields, parent_id):
        assert fields['component_id'] and parent_id

    def validate_package_spec(self, fields, parent_id):
        assert fields['package_id'] and parent_id


class StructureTests(unittest.TestCase):
    def test_live_sources(self):
        result = compiler.compile_structure(selection(CONTROL), Model())
        self.assertTrue({'C14', 'C59', 'C62'} <= result['components'].keys())
        runtime = result['components']['C62']
        self.assertEqual(runtime['parent'], 'C59')
        self.assertEqual(runtime['ref'], 'AN-S-3088@1')
        self.assertEqual(runtime['source_path'], 'LAYER_3_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/AN-S-3088-SPEC-COMPONENT_MANIFEST--declare-manifest-runtime.md')
        self.assertEqual(runtime['sha256'], hashlib.sha256((CONTROL / runtime['source_path']).read_bytes()).hexdigest())
        self.assertEqual(result['project']['ref'], selection(CONTROL).manifest_ref)
        self.assertEqual(result['project']['sha256'], selection(CONTROL).manifest_sha256)
        self.assertEqual(result['components']['C14']['parent'], 'C00')
        self.assertEqual(result['components']['C14']['source_path'], COMPONENT.name)
        self.assertEqual(json.loads(json.dumps(result)), result)
        snapshot = parse_structure(json.dumps(result).encode())
        self.assertEqual(snapshot.packages['pkg1'].component, 'C62')
        self.assertEqual(snapshot.packages['pkg1'].ref, 'AN-S-3089@1')

    def test_pin_duplicates_parent_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            shutil.copyfile(PROJECT, project)
            shutil.copyfile(COMPONENT, child)
            (control / '__EXAMPLE_C14').mkdir()
            selected = selection(control)
            result = compiler.compile_structure(selected, Model())
            self.assertEqual(result['project']['sha256'], selected.manifest_sha256)
            selected.manifest_ref = 'AN-S-3037@99'
            with self.assertRaisesRegex(ValueError, 'pin changed'):
                compiler.compile_structure(selected, Model())
            selected.manifest_ref = selection(control).manifest_ref
            duplicate = control / 'AN-S-4000-SPEC-PROJECT_MANIFEST--duplicate.md'
            duplicate.write_text(project.read_text().replace('AN-S-3037', 'AN-S-4000'))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                compiler.compile_structure(selected, Model())
            duplicate.unlink()
            child.write_text(child.read_text().replace('component: C00', 'component: C14'))
            with self.assertRaisesRegex(ValueError, 'identity or parent'):
                compiler.compile_structure(selected, Model())
            shutil.copyfile(COMPONENT, child)
            (control / 'FIRST_C14').mkdir()
            (control / 'SECOND_C14').mkdir()
            with self.assertRaisesRegex(ValueError, 'Duplicate Component directory'):
                compiler.compile_structure(selected, Model())
            (control / 'FIRST_C14').rmdir()
            (control / 'SECOND_C14').rmdir()
            class MutatingModel(Model):
                def validate_component_manifest(self, fields, parent_id):
                    child.write_text(child.read_text() + '\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                compiler.compile_structure(selected, MutatingModel())

    def test_canonical_component_classified_by_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            raw = COMPONENT.read_text()
            _, frontmatter, body = raw.split('---', 2)
            header = canonical_native_header(yaml.safe_load(frontmatter))
            path = control / 'AN-S-3039-SPEC-OTHER--engine.md'
            path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
            result = compiler.compile_structure(selection(control), Model())
            self.assertEqual(path.name, result['components']['C14']['source_path'])

    def test_formal_fields(self):
        claim = '''## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import ComponentManifest\ndeclare_entity(entity_name="Component Manifest", instance=ComponentManifest(component_id="C1", name="One", lens_whitelist=["SPEC"]))\n```\n'''
        self.assertEqual(compiler._fields(claim), {'component_id': 'C1', 'name': 'One', 'lens_whitelist': ['SPEC']})


if __name__ == '__main__':
    unittest.main()
