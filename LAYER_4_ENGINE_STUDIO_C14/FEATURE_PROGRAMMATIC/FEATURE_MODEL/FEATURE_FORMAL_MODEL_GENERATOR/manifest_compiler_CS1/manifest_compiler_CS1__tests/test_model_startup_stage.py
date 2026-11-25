import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ..compiler import compile_ingested
from ..model_startup import select_model_rows, stage_model


def inputs(**changes):
    return {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None, **changes}


class ModelStartupStageTests(unittest.TestCase):
    def test_sql_selection_and_sticky_fallback(self):
        def row(path, status):
            return {'source_path': path, 'exact_ref': 'AN-S-1@1',
                    'metadata': {'state': {'status': status}}, 'body': 'body'}
        active = row('LAYER_1_META_ONTOLOGY_C9/_SPEC/a.md', 'active')
        des = row('LAYER_1_META_ONTOLOGY_C9/_DES/content.md', 'active')
        nested = row('ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9/_SPEC/n.md', 'active')
        self.assertEqual([des, active, nested], select_model_rows([active, des, nested, row('other/a.md', 'active'),
                                                       row('LAYER_1_META_ONTOLOGY_C9/b.md', 'draft'),
                                                       row('LAYER_1_META_ONTOLOGY_C9/_DES/deep/other.md', 'active')]))
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            stage_model(Path(first), inputs(), None, [])
            accepted = json.loads((Path(first) / 'model.json').read_text())
            diagnostics = []
            stage_model(Path(second), inputs(has_c9=True, accepted_model=accepted), accepted, diagnostics)
            self.assertEqual(accepted['model_sha256'], json.loads((Path(second) / 'model.json').read_text())['model_sha256'])
            self.assertEqual(1, len(diagnostics))

    def test_tampered_accepted_model_fails_and_retains_candidate_diagnostic(self):
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            stage_model(Path(first), inputs(), None, [])
            accepted = json.loads((Path(first) / 'model.json').read_text())
            accepted['module_sources']['__init__.py'] = 'tampered'
            result = compile_ingested(SimpleNamespace(generation=Path(second).resolve()), inputs(has_c9=True, accepted_model=accepted))
            self.assertIn('error', result)
            self.assertIn('hash mismatch', result['error']['message'])
            self.assertEqual(1, len(result['model_diagnostics']))

    def test_structure_rejection_falls_back_and_hard_failure_keeps_diagnostics(self):
        with TemporaryDirectory() as stage:
            args = SimpleNamespace(generation=Path(stage).resolve(), project_root=Path('/'), control_root='x', project_manifest_sha256='sha')
            with patch('FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler.resolve_native_project',
                       side_effect=ValueError('structure rejected')):
                result = compile_ingested(args, inputs())
            self.assertIn('error', result)
            self.assertEqual('structure rejected', result['error']['message'])
            self.assertEqual(1, len(result['model_diagnostics']))

    def test_envelope_validation(self):
        with TemporaryDirectory() as stage:
            result = compile_ingested(SimpleNamespace(generation=Path(stage).resolve()), {'rows': []})
            self.assertIn('error', result)
            self.assertEqual([], result['model_diagnostics'])
