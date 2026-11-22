import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[6]
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import structure_compile__shared as compiler  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header, native_header_view  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier  # noqa: E402

CONTROL = ROOT / '_anechoic_anechoic'
if (ROOT.parent / 'native-control').is_dir():
    CONTROL = ROOT.parent / 'native-control'
PROJECT = ROOT / 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
COMPONENT = CONTROL / '_SPEC/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md'


def selection(control):
    project = PROJECT if control == CONTROL else control / PROJECT.name
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

    def validate_component_seed_manifest(self, fields, parent_id):
        assert fields['component_seed_id'] and parent_id


class StructureTests(unittest.TestCase):
    def test_live_sources(self):
        result = compiler.compile_structure(selection(CONTROL), Model())
        self.assertTrue({'C14', 'C59', 'C62'} <= result['components'].keys())
        runtime = result['components']['C62']
        self.assertEqual(runtime['parent'], 'C59')
        runtime_header = native_header_view(parse_carrier((CONTROL / runtime['source_path']).read_bytes(), CONTROL / runtime['source_path']).metadata)
        self.assertEqual(runtime['ref'], f"AN-S-3088@{runtime_header['state']['version']}")
        self.assertEqual(runtime['source_path'], 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/_SPEC/AN-S-3088-SPEC-COMPONENT_MANIFEST--declare-manifest-runtime.md')
        self.assertEqual(runtime['sha256'], hashlib.sha256((CONTROL / runtime['source_path']).read_bytes()).hexdigest())
        self.assertEqual(result['project']['ref'], selection(CONTROL).manifest_ref)
        self.assertEqual(result['project']['sha256'], selection(CONTROL).manifest_sha256)
        self.assertEqual(result['components']['C14']['parent'], 'C00')
        self.assertEqual(result['components']['C14']['source_path'], f'_SPEC/{COMPONENT.name}')
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertEqual(result['packages']['CS1']['component'], 'C50')
        self.assertEqual(result['packages']['CS1']['ref'], 'AN-S-3089@4')

    def test_pin_duplicates_parent_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            shutil.copyfile(PROJECT, project)
            child.write_text(COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1))
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
            child.write_text(COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1))
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

    def test_component_manifest_in_spec_and_duplicate_across_layouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            spec = control / '_SPEC'
            spec.mkdir()
            content = COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1)
            (spec / COMPONENT.name).write_text(content)
            result = compiler.compile_structure(selection(control), Model())
            self.assertEqual(result['components']['C14']['source_path'], f'_SPEC/{COMPONENT.name}')
            (control / COMPONENT.name).write_text(content)
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                compiler.compile_structure(selection(control), Model())

    def test_canonical_component_classified_by_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            raw = COMPONENT.read_text()
            _, frontmatter, body = raw.split('---', 2)
            header = canonical_native_header(yaml.safe_load(frontmatter))
            header['tier'] = 4
            path = control / 'AN-S-3039-SPEC-OTHER--engine.md'
            path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
            result = compiler.compile_structure(selection(control), Model())
            self.assertEqual(path.name, result['components']['C14']['source_path'])

    def test_component_carrier_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            (control / COMPONENT.name).symlink_to(COMPONENT)
            with self.assertRaises(OSError):
                compiler.compile_structure(selection(control), Model())

    def test_component_manifest_requires_tier_four(self):
        raw = COMPONENT.read_text()
        _, frontmatter, body = raw.split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 4
        carrier = parse_carrier(f'---\n{yaml.safe_dump(header)}---{body}'.encode(), COMPONENT)
        fields = compiler._component_inputs(COMPONENT, carrier, 'C00', 'AN')
        self.assertEqual(fields['tier'], 4)
        header['tier'] = 0
        carrier = parse_carrier(f'---\n{yaml.safe_dump(header)}---{body}'.encode(), COMPONENT)
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            compiler._component_inputs(COMPONENT, carrier, 'C00', 'AN')

    def test_formal_fields(self):
        claim = '''## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import ComponentManifest\ndeclare_entity(entity_name="Component Manifest", instance=ComponentManifest(component_id="C1", name="One", lens_whitelist=["SPEC"]))\n```\n'''
        self.assertEqual(compiler._fields(claim), {'component_id': 'C1', 'name': 'One', 'lens_whitelist': ['SPEC']})


if __name__ == '__main__':
    unittest.main()
