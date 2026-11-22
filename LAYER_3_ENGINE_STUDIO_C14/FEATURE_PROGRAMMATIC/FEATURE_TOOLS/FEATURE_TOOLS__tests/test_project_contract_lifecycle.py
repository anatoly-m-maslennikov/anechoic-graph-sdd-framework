from hashlib import sha256
from pathlib import Path
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import read_active_model_sources
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import _NativeModel
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.common import InputError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import change_spec_status
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests import test_native_lifecycle_draft as fixtures

ROOT = Path(__file__).resolve().parents[4] / '_anechoic_anechoic'
BODY = '\n## Summary\n\nExample\n\n## Guarantee\n\nThe output is available.\n'


class ProjectContractLifecycleTests(LifecycleRouteSupport, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = _NativeModel(records=read_active_model_sources(ROOT, ROOT / 'LAYER_1_META_ONTOLOGY_C9'))

    def test_create_promote_and_activate_validate_guarantee(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
        project.manifest_sha256 = sha256(project.manifest_path.read_bytes()).hexdigest()
        rows = lambda: capture_native(project).atoms
        validate = self.model.validate_project_spec
        values = {'template': 'project_contract', 'container': {'component': 'C00'}, 'lens': 'SPEC', 'body': BODY}
        for body in ('\n## Summary\n\nExample\n', BODY.replace('The output is available.', '   '), BODY + '\n## Guarantee\n\nDuplicate\n'):
            with self.subTest(body=body), self.assertRaises(InputError):
                create_draft(project, {'newAtom': {**values, 'body': body}}, current_rows=rows(), validate_project_spec_model=validate)
        for invalid in ({'tier': 1}, {'container': {'component': 'C9'}}):
            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                create_draft(project, {'newAtom': {**values, **invalid}}, current_rows=rows(), validate_project_spec_model=validate)
        draft = create_draft(project, {'newAtom': values}, current_rows=rows(), validate_project_spec_model=validate)['savedDraft']
        path = project.root / draft['path']
        path.write_text(path.read_text().replace('The output is available.', ' '))
        target = {'ref_id': draft['ref_id'], 'version': 1}
        with self.assertRaises(InputError):
            promote_draft(project, {'target': target, 'targetStatus': 'ready'}, current_rows=rows(), validate_project_spec_model=validate)
        path.write_text(path.read_text().replace('## Guarantee\n\n \n', '## Guarantee\n\nThe output is available.\n'))
        ready = promote_draft(project, {'target': target, 'targetStatus': 'ready'}, current_rows=rows(), validate_project_spec_model=validate)['artifact']
        path = project.root / ready['path']
        path.write_text(path.read_text().replace('The output is available.', ' '))
        with self.assertRaises(InputError):
            change_spec_status(project, {'target': {'ref_id': ready['ref_id'], 'version': 1}, 'targetStatus': 'active'}, current_rows=rows(), validate_project_spec_model=validate)
        path.write_text(path.read_text().replace('## Guarantee\n\n \n', '## Guarantee\n\nThe output is available.\n'))
        result = change_spec_status(project, {'target': {'ref_id': ready['ref_id'], 'version': 1}, 'targetStatus': 'active'}, current_rows=rows(), validate_project_spec_model=validate)
        self.assertEqual(result['artifact']['status'], 'active')
