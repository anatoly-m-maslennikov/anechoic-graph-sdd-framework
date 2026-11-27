from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ..spec_staging import _stage_spec_rows


class SpecStagingTests(unittest.TestCase):
    def test_staging_uses_database_rows_for_model(self):
        staged = {'source_path': 'control/__PROJECT_CONFIG/CUSTOM_MODEL/c.md', 'exact_ref': 'AN-C-1@1',
                  'metadata': {'db': True}, 'body': 'from db', 'sha256': 'a' * 64}
        calls = []
        class Response:
            def __init__(self, value): self.value = value
            def raise_for_status(self): pass
            def json(self): return {'result': self.value}
        class Client:
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def put(self, path, json):
                calls.append((path, json))
                return Response({'snapshot_id': 'snap'})
            def get(self, path, params):
                calls.append((path, params))
                return Response({'snapshot_id': 'snap', 'rows': [staged]})
        inputs = {'rows': [{'source_path': '__PROJECT_CONFIG/CUSTOM_MODEL/c.md', 'exact_ref': 'old',
                            'metadata': {}, 'body': 'old'}], 'spec_rows': [staged], 'manifest_path': 'manifest.md'}
        with patch('WORKERS_beta_C69.spec_staging.httpx2.Client', Client):
            result = _stage_spec_rows({'control_root': 'control', 'manifest_sha256': 'b' * 64}, inputs,
                                      {'socket': '/tmp/spec.sock', 'instance_id': 'instance'})
        assert result['snapshot_id'] == 'snap'
        assert result['rows'][0]['body'] == 'from db'
        assert result['rows'][0]['metadata'] == {'db': True}
        assert calls[0][1] == {'instance_id': 'instance', 'manifest_sha256': 'b' * 64, 'rows': [staged]}
        assert calls[1][1] == {'instance_id': 'instance', 'snapshot_id': 'snap'}


    def test_refusal_reuses_staged_rows(self):
        tmp_path = Path(self.enterContext(TemporaryDirectory()))
        from .. import WORKERS_beta_C69__shared as worker
        source = {'accepted_model': None, 'spec_database': {'socket': '/tmp/spec.sock', 'instance_id': 'i'}}
        staged = {'rows': [], 'spec_rows': [{'body': 'staged'}]}
        attempts = []
        def compile_ingested(binding, stage, inputs, source, **kwargs):
            attempts.append(inputs)
            (stage / "model.json").write_text('{"bindings": {}}')
            return None, None, {}, []
        def finish(endpoints, domains):
            if len(attempts) == 1:
                raise ValueError('refused')
            return 'captured'
        with patch.object(worker, '_stage_spec_rows', return_value=staged) as stage, \
             patch.object(worker, '_compile_ingested', side_effect=compile_ingested):
            _, captured = worker._compile_and_capture({}, tmp_path, {}, source, finish)
        assert captured == 'captured'
        assert attempts == [staged, staged]
        assert stage.call_count == 1

    def test_compiled_model_domains_reach_full_snapshot(self):
        import json
        from .. import WORKERS_beta_C69__shared as worker
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        declarations = [[name, {"arguments": {"entity_name": "Status", "entity_kind": "Property",
                         "relation_name": "IS_PROPERTY_OF", "base_path": root + ".Header.State",
                         "applies_to_entity_classes": [root + "//" + name], "allowed_values": values}}]
                        for name, values in (("Specification", ["draft", "active", "archived"]),
                                             ("Ticket", ["draft", "active", "reviewed", "archived"]),
                                             ("project_config", ["draft", "active", "archived"]))]
        with TemporaryDirectory() as directory:
            stage = Path(directory)
            def compile_model(binding, path):
                (path / "model.json").write_text(json.dumps({"bindings": {"declarations": declarations}}))
                return {}, {}, {"edge": {}}
            def finish(endpoints, domains):
                self.assertEqual({"edge": {}}, endpoints)
                self.assertIn("reviewed", domains["T"])
                self.assertNotIn("unknown", domains["T"])
                return "captured"
            with patch.object(worker, "_compile", side_effect=compile_model):
                _, result = worker._compile_and_capture({}, stage, None, None, finish)
            self.assertEqual("captured", result)

    def test_structure_ingestion_issue_rejects_before_staging(self):
        inputs = {'structure_issues': [{'relative_path': 'control/bad.md', 'message': 'bad context'}]}
        with self.assertRaisesRegex(ValueError, 'Structure source ingestion failed'):
            _stage_spec_rows({}, inputs, {})

    def test_snapshot_identity_reaches_compiler_admissions(self):
        import io
        import json
        import sys
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import compile_project__pub as compiler
        row = {'source_path': 'control/model.md', 'exact_ref': 'AN-S-1@1',
               'metadata': {}, 'body': 'body', 'sha256': 'a' * 64}
        raw = {'snapshot_id': 'snap', 'spec_rows': [row], 'manifest_path': 'manifest.md',
               'rows': [{**{k: row[k] for k in ('exact_ref', 'metadata', 'body')}, 'source_path': 'model.md'}],
               'structure_alias_issues': [{'relative_path': 'control/AN-S-2-SPEC-OTHER--x.md',
                                           'template': 'new_component'}]}
        observed = []
        def admit(args, structure, *, compile_snapshot):
            payload = json.load(sys.stdin)
            observed.append(payload['rows'])
            with patch.object(compiler, 'compile_structure_rows', return_value='structure') as compile_rows:
                observed.append(compile_snapshot(args, None, payload['spec_rows'], payload['manifest_path']))
            assert compile_rows.call_args.kwargs['alias_issues'] == raw['structure_alias_issues']
            print(json.dumps({'structure': 'structure'}))
        args = Namespace(control_root='control', project_root='.',
                         project_manifest_sha256='b' * 64)
        output = io.StringIO()
        with patch.object(sys, 'stdin', io.StringIO(json.dumps(raw))), \
             patch.object(sys, 'stdout', output), patch.object(compiler, 'compile_ingested_cli', side_effect=admit):
            compiler._compile_ingested(args)
        assert observed == [raw['rows'], 'structure']
        assert json.loads(output.getvalue())['snapshot_id'] == 'snap'
        for snapshot_id in ('', ' ', '\u00a0\u2003'):
            invalid = json.dumps({**raw, 'snapshot_id': snapshot_id})
            with patch.object(sys, 'stdin', io.StringIO(invalid)), self.assertRaisesRegex(
                    ValueError, 'Missing Spec snapshot identity'):
                compiler._compile_ingested(args)
        raw['rows'][0]['body'] = 'tampered'
        with patch.object(sys, 'stdin', io.StringIO(json.dumps(raw))):
            with self.assertRaisesRegex(ValueError, 'does not match Spec snapshot snap'):
                compiler._compile_ingested(args)

    def test_structure_alias_failure_does_not_retry_model(self):
        import io
        import json
        import sys
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import compile_project__pub as compiler
        raw = {'snapshot_id': 'snap', 'spec_rows': [], 'manifest_path': 'manifest.md', 'rows': [],
               'structure_alias_issues': [{'relative_path': 'control/AN-S-2-SPEC-OTHER--x.md',
                                           'template': 'new_component'}]}
        calls = []
        def admit(args, structure, *, compile_snapshot):
            calls.append(json.load(sys.stdin))
            compile_snapshot(args, object(), [], 'manifest.md')
        args = Namespace(control_root='control', project_root='.',
                         project_manifest_sha256='b' * 64)
        with patch.object(sys, 'stdin', io.StringIO(json.dumps(raw))), \
             patch.object(compiler, 'compile_ingested_cli', side_effect=admit), \
             patch.object(compiler, 'compile_structure_rows', side_effect=compiler.StructureAdmissionError('bad alias')):
            with self.assertRaisesRegex(compiler.StructureAdmissionError, 'bad alias'):
                compiler._compile_ingested(args)
        assert len(calls) == 1
        assert 'structure_alias_issues' not in calls[0]

    def test_structure_admission_error_bypasses_model_fallback(self):
        import importlib
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import compile_project__pub as compiler
        ingestion = importlib.import_module(compiler.compile_ingested_cli.__module__)
        with TemporaryDirectory() as directory:
            args = Namespace(generation=Path(directory).resolve())
            raw = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None}
            with patch.object(ingestion, '_stage', return_value='digest') as stage, \
                 patch.object(ingestion, '_structure', side_effect=compiler.StructureAdmissionError('bad alias')), \
                 patch.object(ingestion, 'mark_startup_timing') as timing:
                with self.assertRaisesRegex(compiler.StructureAdmissionError, 'bad alias'):
                    ingestion.compile_ingested(args, raw, None)
            assert stage.call_count == 1
            timing.assert_not_called()
