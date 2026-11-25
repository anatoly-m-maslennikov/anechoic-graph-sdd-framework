import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68.lifecycle_queries import lifecycle_sql, lifecycle_context


def database():
    db = duckdb.connect()
    db.execute('CREATE TABLE generation(id VARCHAR, model VARCHAR)')
    db.execute('INSERT INTO generation VALUES (?, ?)', ['g', json.dumps({'ticket_labels': ['TASK']})])
    db.execute('CREATE TABLE atoms(reference VARCHAR, relative_path VARCHAR, filename VARCHAR, status_group VARCHAR, "header.state.version" BIGINT, "header.state.status" VARCHAR)')
    db.execute('CREATE TABLE native_references(reference VARCHAR, exact_ref VARCHAR)')
    db.execute('CREATE TABLE relations(source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR, target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)')
    db.execute('CREATE TABLE generation_carriers(hashes VARCHAR)')
    db.execute('CREATE TABLE lifecycle_lenses(reference VARCHAR, lens VARCHAR)')
    atoms = [('AN-T-1', 'AN-T-1@1', 'Current', 1, 'active'),
             ('AN-T-1@2-draft', 'AN-T-1@2-draft', 'Draft', 2, 'draft'),
             ('AN-T-2', 'AN-T-2@1', 'Current', 1, 'active'),
             ('AN-T-3', 'AN-T-3@1', 'Current', 1, 'active'),
             ('AN-S-99999999999999999999', 'AN-S-99999999999999999999@1', 'Current', 1, 'ready')]
    for ref, exact, group, version, status in atoms:
        db.execute('INSERT INTO atoms VALUES (?, ?, ?, ?, ?, ?)', [ref, '.', ref + '.md', group, version, status])
        db.execute('INSERT INTO native_references VALUES (?, ?)', [ref, exact])
    db.execute('INSERT INTO generation_carriers VALUES (?)', [json.dumps({ref+'.md': 'a'*64 for ref, *_ in atoms})])
    for source, target in [('AN-T-1', 'AN-T-2'), ('AN-T-2', 'AN-T-3'), ('AN-T-3', 'C00')]:
        db.execute('INSERT INTO relations VALUES (?, ?, ?, ?, ?, false)', ['Atom', source, 'Component' if target == 'C00' else 'Atom', target, 'IS_CONTAINED_BY'])
    db.execute("INSERT INTO lifecycle_lenses VALUES ('AN-T-1', 'DES'), ('AN-T-2', 'DES')")
    return db


def test_scoped_recursive_context_and_number_allocation():
    db = database()
    row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'sourceCurrent': {'ref_id': 'AN-T-1'}, 'newAtom': {'template': 'task'}})).fetchone()
    carriers = json.loads(row[5])
    assert {c['id'] for c in carriers} == {'AN-T-1', 'AN-T-2', 'AN-T-3'}
    assert next(c for c in carriers if c['_exact_ref'] == 'AN-T-1@2-draft')['read'] is False
    assert next(c for c in carriers if c['ref'] == 'AN-T-1')['owner_ref'] == 'AN-T-2'
    assert row[3:5] == ('3', '99999999999999999999')
    assert json.loads(row[7]) == ['DES']


def test_untrusted_selectors_are_literals():
    db = database()
    row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': "x' OR TRUE --"}})).fetchone()
    assert json.loads(row[5]) == []


def test_context_checks_generation():
    row = database().execute(lifecycle_sql('AN', 'atom_lifecycle_update', {})).fetchone()
    class Response:
        status = 200
        def read(self):
            return json.dumps({'result': {'rows': [list(row)]}}).encode()
    class Connection:
        def __init__(self, _): pass
        def request(self, *args): pass
        def getresponse(self): return Response()
        def close(self): pass
    with patch('ORCHESTRATOR_beta_C68.lifecycle_queries.UnixConnection', Connection), \
         patch('ORCHESTRATOR_beta_C68.lifecycle_queries.read_structure', return_value={}) as read:
        assert lifecycle_context('/x', 'i', 'g', 'AN', 'atom_lifecycle_update', {})['model'] is None
        read.assert_called_once_with('/x', 'i', {'base_generation': 'g'})
        read.return_value = None
        with unittest.TestCase().assertRaisesRegex(ValueError, 'generation changed'):
            lifecycle_context('/x', 'i', 'g', 'AN', 'atom_lifecycle_update', {})
        try:
            lifecycle_context('/x', 'i', 'other', 'AN', 'atom_lifecycle_update', {})
        except ValueError:
            pass
        else:
            assert False, 'stale generation accepted'


class LifecycleQueryTests(unittest.TestCase):
    def test_trimmed_model_binds_and_validates_spec(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_serialized_model
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header

        with TemporaryDirectory() as directory:
            root = Path(directory)
            engine = Path(__file__).resolve().parents[2]
            compiler = ('FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.'
                        'manifest_compiler_CS1.image_model_compile')
            subprocess.run([sys.executable, '-B', '-P', '-m', compiler, str(root)],
                           env={**os.environ, 'PYTHONPATH': str(engine)}, capture_output=True, check=True)
            model = json.loads((root / 'model.json').read_text())
            model['module_sources'] = {name: (root / 'anechoic_runtime_model' / name).read_text()
                                       for name in model['modules']}
            model['ticket_labels'] = ['TASK']
            db = database()
            db.execute('UPDATE generation SET model = ?', [json.dumps(model)])
            row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft',
                                          {'newAtom': {'template': 'axiom'}})).fetchone()
            trimmed = json.loads(row[1])
            self.assertEqual({k: v for k, v in model.items() if k not in {'declarations', 'ticket_labels'}}, trimmed)
            self.assertEqual(['TASK'], json.loads(row[2]))
            header = canonical_native_header({'identity': {'atom_id': 'AN-S-1'},
                'context': {'container': {'component': 'C00'}, 'template': 'axiom', 'lens': 'SPEC', 'tier': 0},
                'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-01-01'}})
            for descriptor in (model, trimmed):
                with open_serialized_model(descriptor) as bound:
                    with self.assertRaisesRegex(ValueError, 'Project SPEC template is not supported'):
                        bound.validate_project_spec('axiom', header, 'C00')

    def test_scoped_context(self):
        test_scoped_recursive_context_and_number_allocation()

    def test_literal_selectors(self):
        test_untrusted_selectors_are_literals()

    def test_generation(self):
        test_context_checks_generation()

    def test_malformed_template_and_revision_allocation(self):
        db = database()
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'newAtom': {'template': []}})).fetchone()
        self.assertEqual(row[3:5], ('3', '99999999999999999999'))
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'sourceCurrent': {'ref_id': 'AN-T-1'}})).fetchone()
        self.assertEqual(row[3:5], ('0', '0'))
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_asset', {'newAtom': {'template': 'note'}})).fetchone()
        self.assertEqual(row[3], '3')

    def test_replacement_marker_is_pinned_to_the_draft_source(self):
        db = database()
        db.execute("INSERT INTO relations VALUES ('Atom', 'AN-T-1@2-draft', 'Atom', 'AN-T-9@1-archived', 'IS_REPLACEMENT_FOR', false)")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_promote_draft',
                                       {'target': {'ref_id': 'AN-T-1@2-draft', 'version': 2}})).fetchone()
        carriers = json.loads(row[5])
        self.assertTrue(next(c for c in carriers if c['ref'] == 'AN-T-1@2-draft')['replaces'])
        self.assertFalse(next(c for c in carriers if c['ref'] == 'AN-T-1')['replaces'])

    def test_child_stub_and_physical_descendants(self):
        db = database()
        db.execute("INSERT INTO atoms VALUES ('AN-T-4', '.', 'AN-T-4.md', 'Current', 1, 'active')")
        db.execute("INSERT INTO native_references VALUES ('AN-T-4', 'AN-T-4@1')")
        db.execute("INSERT INTO relations VALUES ('Atom', 'AN-T-4', 'Atom', 'AN-T-1', 'IS_CONTAINED_BY', false)")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': 'AN-T-1'}})).fetchone()
        child = next(c for c in json.loads(row[5]) if c['ref'] == 'AN-T-4' and c['owner_ref'] == 'AN-T-1')
        self.assertTrue(row[6])
        self.assertFalse(child['read'])
        self.assertIsNone(child['_source_sha256'])
        db.execute("DELETE FROM relations WHERE source_ref='AN-T-4' AND target_ref='AN-T-1'")
        db.execute("UPDATE atoms SET relative_path='AN-T-1' WHERE reference='AN-T-3'")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': 'AN-T-1'}})).fetchone()
        self.assertTrue(row[6])
