import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[6]
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import compile_structure  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CarrierError, LimitReached, ReadContext, canonical_native_header, native_header_view  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_manifest__pub import manifest_summary_fields  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import resolve_native_project  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.structure_compile import _validation_fields  # noqa: E402

CONTROL = ROOT / '_anechoic_anechoic'
if (ROOT.parent / 'native-control').is_dir():
    CONTROL = ROOT.parent / 'native-control'
PROJECT = ROOT / 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
COMPONENT = CONTROL / '_SPEC/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md'


def selection(control, project=None):
    if project is None:
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
    def test_project_summary_follows_model_declaration(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model
        model = load_native_model()
        def validate(fields, parent):
            self.assertEqual('Declare Anechoic', fields.pop('summary'))
            return model.validate_manifest(fields, parent)
        resolve_native_project(ROOT, CONTROL.name, validate_manifest=validate, require_manifest_summary=True)
        resolve_native_project(ROOT, CONTROL.name, validate_manifest=model.validate_manifest)
        self.assertEqual({}, manifest_summary_fields(SimpleNamespace(body='## Claim\n\nText\n')))
        with self.assertRaisesRegex(ValueError, 'duplicate Summary'):
            manifest_summary_fields(SimpleNamespace(body='## Summary\n\nOne\n\n## Summary\n\nTwo\n'))

    def test_component_and_seed_summary_follows_model_declaration(self):
        carrier = SimpleNamespace(body='## Summary\n\nAuthored summary.\n', metadata={})
        model = SimpleNamespace(requires_atom_state=False, declares_summary=lambda name: name == 'Component Manifest')
        self.assertEqual({'summary': 'Authored summary.'}, _validation_fields({}, carrier, model, 'Component Manifest'))
        self.assertEqual({}, _validation_fields({}, carrier, model, 'Component Seed Manifest'))
        self.assertEqual({}, _validation_fields({}, carrier, Model(), 'Component Manifest'))
        model.declares_summary = lambda _: True
        seed = SimpleNamespace(body='# Manifest Build\n\n## Purpose\n\nBuild.\n', metadata={})
        self.assertEqual({'summary': 'Manifest Build'}, _validation_fields({}, seed, model, 'Component Seed Manifest'))
        for body in ('## Purpose\n\nBuild.\n', '# One\n\n# Two\n'):
            with self.assertRaisesRegex(ValueError, 'requires one title'):
                _validation_fields({}, SimpleNamespace(body=body, metadata={}), model, 'Component Seed Manifest')

    def _standalone_project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control, project = root / "control", root / PROJECT.name
        (control / "_SPEC").mkdir(parents=True)
        shutil.copyfile(PROJECT, project)
        return control, selection(control, project)

    def test_ordinary_specs_may_be_malformed_unreadable_or_oversized(self):
        control, selected = self._standalone_project()
        spec = control / "_SPEC"
        child = spec / COMPONENT.name
        child.write_text(COMPONENT.read_text().replace("tier: 0\n", "tier: 4\n", 1))
        (control / "AN-S-4000-SPEC-REQUIREMENT--bad.md").write_text("---\ninvalid: [\n---\n")
        (spec / "AN-S-4001-SPEC-REQUIREMENT--unreadable.md").symlink_to(spec / "missing.md")
        oversized = spec / "AN-S-4002-SPEC-REQUIREMENT--oversized.md"
        oversized.touch()
        read = ReadContext.read

        def limited(reader, path, **options):
            if path == oversized:
                raise LimitReached("max_file_bytes")
            return read(reader, path, **options)

        with patch.object(ReadContext, "read", limited):
            result = compile_structure(selected, Model())
        self.assertEqual(f"_SPEC/{COMPONENT.name}", result["components"]["C14"]["source_path"])

    def test_conventional_structure_manifests_still_require_readable_valid_headers(self):
        control, selected = self._standalone_project()
        for filename in (COMPONENT.name, "AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--required.md"):
            with self.subTest(filename=filename):
                path = control / "_SPEC" / filename
                path.write_text("---\ninvalid: [\n---\n")
                with self.assertRaises(CarrierError):
                    compile_structure(selected, Model())
                path.unlink()

    def test_live_sources(self):
        result = compile_structure(selection(CONTROL), Model())
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
        seed = CONTROL / result['packages']['CS1']['source_path']
        seed_header = native_header_view(parse_carrier(seed.read_bytes(), seed).metadata)
        self.assertEqual(result['packages']['CS1']['ref'], f"AN-S-3089@{seed_header['state']['version']}")

    def test_pin_duplicates_parent_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            shutil.copyfile(PROJECT, project)
            child.write_text(COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1))
            (control / '__EXAMPLE_C14').mkdir()
            selected = selection(control)
            result = compile_structure(selected, Model())
            self.assertEqual(result['project']['sha256'], selected.manifest_sha256)
            selected.manifest_ref = 'AN-S-3037@99'
            with self.assertRaisesRegex(ValueError, 'pin changed'):
                compile_structure(selected, Model())
            selected.manifest_ref = selection(control).manifest_ref
            duplicate = control / 'AN-S-4000-SPEC-PROJECT_MANIFEST--duplicate.md'
            duplicate.write_text(project.read_text().replace('AN-S-3037', 'AN-S-4000'))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                compile_structure(selected, Model())
            duplicate.unlink()
            child.write_text(child.read_text().replace('component: C00', 'component: C14'))
            with self.assertRaisesRegex(ValueError, 'identity or parent'):
                compile_structure(selected, Model())
            child.write_text(COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1))
            (control / 'FIRST_C14').mkdir()
            (control / 'SECOND_C14').mkdir()
            with self.assertRaisesRegex(ValueError, 'Duplicate Component directory'):
                compile_structure(selected, Model())
            (control / 'FIRST_C14').rmdir()
            (control / 'SECOND_C14').rmdir()
            class MutatingModel(Model):
                def validate_component_manifest(self, fields, parent_id):
                    child.write_text(child.read_text() + '\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                compile_structure(selected, MutatingModel())

    def test_component_manifest_in_spec_and_duplicate_across_layouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            spec = control / '_SPEC'
            spec.mkdir()
            content = COMPONENT.read_text().replace('tier: 0\n', 'tier: 4\n', 1)
            (spec / COMPONENT.name).write_text(content)
            result = compile_structure(selection(control), Model())
            self.assertEqual(result['components']['C14']['source_path'], f'_SPEC/{COMPONENT.name}')
            (control / COMPONENT.name).write_text(content)
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                compile_structure(selection(control), Model())

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
            result = compile_structure(selection(control), Model())
            self.assertEqual(path.name, result['components']['C14']['source_path'])

    def test_component_carrier_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            (control / COMPONENT.name).symlink_to(COMPONENT)
            with self.assertRaises(OSError):
                compile_structure(selection(control), Model())

    def test_component_manifest_requires_tier_four(self):
        control, selected = self._standalone_project()
        path = control / '_SPEC' / COMPONENT.name
        raw = COMPONENT.read_text()
        _, frontmatter, body = raw.split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 4
        path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
        fields = compile_structure(selected, Model())['components']['C14']['fields']
        self.assertEqual(fields['tier'], 4)
        header['tier'] = 0
        path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            compile_structure(selected, Model())

    def test_formal_fields(self):
        claim = '''## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import ComponentManifest\ndeclare_entity(entity_name="Component Manifest", instance=ComponentManifest(component_id="C1", name="One", lens_whitelist=["SPEC"]))\n```\n'''
        control, selected = self._standalone_project()
        _, frontmatter, _ = COMPONENT.read_text().split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 4
        path = control / '_SPEC' / COMPONENT.name
        path.write_text(f'---\n{yaml.safe_dump(header)}---\n{claim}')
        fields = compile_structure(selected, Model())['components']['C1']['fields']
        self.assertEqual({key: fields[key] for key in ('component_id', 'name', 'lens_whitelist')},
                         {'component_id': 'C1', 'name': 'One', 'lens_whitelist': ['SPEC']})


if __name__ == '__main__':
    unittest.main()
