import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68.lifecycle_queries import lifecycle_sql, lifecycle_context


def database():
    db = duckdb.connect()
    db.execute('CREATE TABLE ops_ingestion_issues(source VARCHAR, atom_ref VARCHAR, relative_path VARCHAR)')
    db.execute('CREATE TABLE generation(id VARCHAR, model VARCHAR, structure VARCHAR)')
    db.execute('INSERT INTO generation VALUES (?, ?, ?)', ['g', json.dumps({'ticket_labels': ['TASK']}), '{}'])
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
        db.execute('INSERT INTO relations VALUES (?, ?, ?, ?, ?, false)', ['Atom', source, 'Component' if target == 'C00' else 'Atom', target, 'CONTAINED_BY'])
    db.execute("INSERT INTO lifecycle_lenses VALUES ('AN-T-1', 'DES'), ('AN-T-2', 'DES')")
    return db


def test_scoped_recursive_context_and_number_allocation():
    db = database()
    row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'sourceCurrent': {'ref_id': 'AN-T-1'}, 'newAtom': {'template': 'task'}})).fetchone()
    carriers = json.loads(row[6])
    assert {c['id'] for c in carriers} == {'AN-T-1', 'AN-T-2', 'AN-T-3'}
    assert next(c for c in carriers if c['_exact_ref'] == 'AN-T-1@2-draft')['read'] is False
    assert next(c for c in carriers if c['ref'] == 'AN-T-1')['owner_ref'] == 'AN-T-2'
    assert row[4:6] == ('3', '99999999999999999999')
    assert json.loads(row[8]) == ['DES']


def test_untrusted_selectors_are_literals():
    db = database()
    row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': "x' OR TRUE --"}})).fetchone()
    assert json.loads(row[6]) == []


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
    with patch('ORCHESTRATOR_beta_C68.lifecycle_queries.UnixConnection', Connection):
        assert lifecycle_context('/x', 'i', 'g', 'AN', 'atom_lifecycle_update', {})['model'] is None
        try:
            lifecycle_context('/x', 'i', 'other', 'AN', 'atom_lifecycle_update', {})
        except ValueError:
            pass
        else:
            assert False, 'stale generation accepted'


class LifecycleQueryTests(unittest.TestCase):
    def test_scoped_context(self):
        test_scoped_recursive_context_and_number_allocation()

    def test_literal_selectors(self):
        test_untrusted_selectors_are_literals()

    def test_generation(self):
        test_context_checks_generation()

    def test_model_omits_declarations_and_duplicate_labels(self):
        db = database()
        db.execute("UPDATE generation SET model=?", [json.dumps({"declarations": [1], "ticket_labels": ["TASK"], "other": 2})])
        sql = lifecycle_sql("AN", "atom_lifecycle_create_draft", {"newAtom": {"template": "axiom"}})
        row = db.execute(sql).fetchone()
        self.assertEqual(json.loads(row[2]), {"other": 2})
        self.assertEqual(json.loads(row[3]), ["TASK"])

    def test_malformed_template_and_revision_allocation(self):
        db = database()
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'newAtom': {'template': []}})).fetchone()
        self.assertEqual(row[4:6], ('3', '99999999999999999999'))
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_draft', {'sourceCurrent': {'ref_id': 'AN-T-1'}})).fetchone()
        self.assertEqual(row[4:6], ('0', '0'))
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_create_asset', {'newAtom': {'template': 'note'}})).fetchone()
        self.assertEqual(row[4], '3')

    def test_allocation_uses_archive_checkpoint_without_archive_rows(self):
        db = database()
        db.execute("CREATE TABLE ops_archive_versions(atom_id VARCHAR, max_version BIGINT)")
        db.execute("INSERT INTO ops_archive_versions VALUES ('AN-T-1', 8), ('AN-T-42', 2)")
        name = 'atom_lifecycle_create_draft'
        revision = {'sourceCurrent': {'ref_id': 'AN-T-1'}}
        sql = lifecycle_sql('AN', name, revision, archive_versions=True)
        self.assertIn('ops_archive_versions', db.get_table_names(sql))
        row = db.execute(sql).fetchone()
        self.assertEqual('8', row[9])
        self.assertEqual('0', db.execute(lifecycle_sql('AN', name, revision)).fetchone()[9])
        creation = {'newAtom': {'template': 'task'}}
        row = db.execute(lifecycle_sql('AN', name, creation, archive_versions=True)).fetchone()
        self.assertEqual('42', row[4])

    def test_child_stub_and_physical_descendants(self):
        db = database()
        db.execute("INSERT INTO atoms VALUES ('AN-T-4', '.', 'AN-T-4.md', 'Current', 1, 'active')")
        db.execute("INSERT INTO native_references VALUES ('AN-T-4', 'AN-T-4@1')")
        db.execute("INSERT INTO relations VALUES ('Atom', 'AN-T-4', 'Atom', 'AN-T-1', 'CONTAINED_BY', false)")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': 'AN-T-1'}})).fetchone()
        child = next(c for c in json.loads(row[6]) if c['ref'] == 'AN-T-4' and c['owner_ref'] == 'AN-T-1')
        self.assertTrue(row[7])
        self.assertFalse(child['read'])
        self.assertIsNone(child['_source_sha256'])
        db.execute("UPDATE relations SET relation_type='IS_CONTAINED_BY' WHERE source_ref='AN-T-4'")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': 'AN-T-1'}})).fetchone()
        child = next(c for c in json.loads(row[6]) if c['ref'] == 'AN-T-4' and c['owner_ref'] == 'AN-T-1')
        self.assertTrue(row[7])
        self.assertFalse(child['read'])
        db.execute("DELETE FROM relations WHERE source_ref='AN-T-4' AND target_ref='AN-T-1'")
        db.execute("UPDATE atoms SET relative_path='AN-T-1' WHERE reference='AN-T-3'")
        row = db.execute(lifecycle_sql('AN', 'atom_lifecycle_update', {'target': {'ref_id': 'AN-T-1'}})).fetchone()
        self.assertTrue(row[7])
