from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import read_active_model_sources
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import _NativeModel
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_manifest__pub import manifest_state_fields
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.common import InputError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import change_spec_status
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests import test_native_lifecycle_draft as fixtures
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport

ROOT = Path(__file__).resolve().parents[4] / '_anechoic_anechoic'


class AxiomTierLifecycleTests(LifecycleRouteSupport, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = _NativeModel(records=read_active_model_sources(ROOT, ROOT / 'LAYER_1_META_ONTOLOGY_C9'))

    def test_model_and_lifecycle_accept_zero_and_reject_minus_one(self):
        project_instance = self.model._validate('Project', {}, {})
        fields = {'atom_id': 'AN-S-900', 'version': 1, 'ref_id': 'AN-S-900@1-draft', 'tier': 0}
        header = canonical_native_header({'identity': {'atom_id': 'AN-S-900'},
            'context': {'container': {'component': 'C00'}, 'template': 'axiom', 'tier': 0, 'lens': 'SPEC'},
            'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-01-01'}})
        fields.update(manifest_state_fields(SimpleNamespace(metadata=header), include_header=self.model.requires_atom_header))
        # Exercise the generated declaration directly, independent of the route guard.
        self.assertEqual(0, self.model._validate('Axiom', fields, {'CONTAINED_BY': [project_instance]}).tier)
        with self.assertRaises(ValueError):
            self.model._validate('Axiom', fields | {'tier': -1}, {'CONTAINED_BY': [project_instance]})

        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
        project.manifest_sha256 = sha256(project.manifest_path.read_bytes()).hexdigest()
        rows = lambda: capture_native(project).atoms
        values = {'template': 'axiom', 'container': {'component': 'C00'}, 'lens': 'SPEC',
                  'body': '\n## Summary\n\nExample\n'}
        with self.assertRaises(InputError):
            create_draft(project, {'newAtom': values | {'tier': -1}}, current_rows=rows(),
                         validate_project_spec_model=self.model.validate_project_spec)
        draft = create_draft(project, {'newAtom': values}, current_rows=rows(),
                             validate_project_spec_model=self.model.validate_project_spec)['savedDraft']
        ready = promote_draft(project, {'target': {'ref_id': draft['ref_id'], 'version': 1}, 'targetStatus': 'ready'},
                              current_rows=rows(), validate_project_spec_model=self.model.validate_project_spec)['artifact']
        active = change_spec_status(project, {'target': {'ref_id': ready['ref_id'], 'version': 1}, 'targetStatus': 'active'},
                                    current_rows=rows(), validate_project_spec_model=self.model.validate_project_spec)['artifact']
        row = next(row for row in rows() if row['id'] == draft['atom_id'])
        self.assertEqual(0, row['header_json']['tier'])
        self.assertEqual(project.control_root, (project.root / active['path']).parent)
