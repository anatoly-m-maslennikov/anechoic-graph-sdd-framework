import unittest

import duckdb

from .. import ingestion_issues, realization_projection
from ..generation import _digest
from ..query_schema import public_schema
from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


class IngestionIssuesTest(unittest.TestCase):
    def test_source_read_issues_follow_realization_scan(self):
        data = _generation()
        data["graph"] = {"nodes": [], "occurrences": [], "edges": [], "test_edges": [],
                         "read_issues": [["bad.py", "unreadable"]]}
        with _server() as client:
            data["receipt"]["graph_sha256"] = _digest(data["graph"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            result = _query(client, "SELECT source, relative_path, code, message FROM main.ops_ingestion_issues")
            self.assertEqual([["realization", "bad.py", "read_error", "unreadable"]], result.json()["result"]["rows"])
            result = _query(client, "SELECT * FROM main.import_read_issues")
            self.assertEqual([["bad.py", "unreadable"]], result.json()["result"]["rows"])
            data["graph"]["read_issues"] = []
            data["receipt"]["graph_sha256"] = _digest(data["graph"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertEqual([], client.get("/ingestion/issues", params=BINDING).json()["result"]["rows"])

    def test_route_before_generation_and_source_replacement(self):
        issue = {"relative_path": "a.md", "code": "invalid", "message": "bad", "atom_ref": None, "related_paths": []}
        with _server() as client:
            self.assertEqual([], client.get('/ingestion/issues', params=BINDING).json()['result']['rows'])
            for source in ('atom', 'build'):
                response = client.put('/ingestion/issues', json={**BINDING, 'source': source, 'issues': [issue]})
                self.assertEqual(200, response.status_code, response.text)
            bad = {**issue, 'related_paths': 'invalid'}
            self.assertEqual(400, client.put('/ingestion/issues', json={**BINDING, 'source': 'atom', 'issues': [bad]}).status_code)
            self.assertEqual(403, client.get('/ingestion/issues', params={'instance_id': 'foreign'}).status_code)
            rows = client.get('/ingestion/issues', params=BINDING).json()['result']['rows']
            self.assertEqual(['atom', 'build'], [row['source'] for row in rows])
            self.assertEqual(200, client.put('/ingestion/issues', json={**BINDING, 'source': 'atom', 'issues': []}).status_code)
            self.assertEqual(['build'], [row['source'] for row in client.get('/ingestion/issues', params=BINDING).json()['result']['rows']])
            self.assertEqual(200, client.put('/generation', json=_generation()).status_code)
            self.assertIn('ops_ingestion_issues', client.get('/schema', params=BINDING).json()['result']['tables'])
            self.assertEqual([], _query(client, 'SELECT source, relative_path FROM main.ops_ingestion_issues').json()['result']['rows'])
            self.assertEqual(400, _query(client, 'DELETE FROM main.ops_ingestion_issues').status_code)

    def test_build_diagnostics_before_and_after_admission(self):
        diagnostic = {"attempt_id": "try", "accepted_generation": "untrusted", "severity": "ERROR",
                      "code": "invalid", "message": "bad Model", "atom_ref": None,
                      "source_path": None, "subject": None}
        payload = {**BINDING, "source": "build", "issues": [], "model_diagnostics": [diagnostic]}
        with _server() as client:
            response = client.put("/ingestion/issues", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            query = "SELECT accepted_generation, code FROM mrt_diag_model_manifests"
            self.assertEqual([[None, "invalid"]], _query(client, query).json()["result"]["rows"])
            self.assertEqual(200, client.put("/ingestion/issues", json=payload).status_code)
            self.assertEqual([["b" * 64, "invalid"]], _query(client, query).json()["result"]["rows"])
            self.assertEqual(400, client.put("/ingestion/issues", json={**payload, "source": "atom"}).status_code)
            self.assertEqual(400, client.put("/ingestion/issues", json={**payload, "model_diagnostics": [{}]}).status_code)
            self.assertEqual([["b" * 64, "invalid"]], _query(client, query).json()["result"]["rows"])
            self.assertEqual(200, client.put("/ingestion/issues", json={**BINDING, "source": "build", "issues": []}).status_code)
            self.assertEqual([["b" * 64, "invalid"]], _query(client, query).json()["result"]["rows"])
            self.assertEqual(200, client.put("/ingestion/issues", json={**payload, "model_diagnostics": []}).status_code)
            self.assertEqual([], _query(client, query).json()["result"]["rows"])

    def test_legacy_migration_and_public_schema(self):
        connection = duckdb.connect()
        self.addCleanup(connection.close)
        connection.execute('CREATE TABLE mrt_diag_import_read_issues (relative_path VARCHAR PRIMARY KEY, error_message VARCHAR NOT NULL)')
        connection.execute("INSERT INTO mrt_diag_import_read_issues VALUES ('bad.py', 'unreadable')")
        connection.execute('CREATE VIEW import_read_issues AS SELECT * FROM mrt_diag_import_read_issues')
        connection.execute('CREATE VIEW mrt_import_read_issues AS SELECT * FROM mrt_diag_import_read_issues')
        connection.execute('BEGIN')
        realization_projection.prepare(connection)
        connection.execute('COMMIT')
        self.assertEqual([('bad.py', 'unreadable')], connection.execute('SELECT * FROM mrt_diag_import_read_issues').fetchall())
        ingestion_issues.initialize(connection)
        self.assertEqual(1, len(ingestion_issues.rows(connection)))
        self.assertEqual('read_error', ingestion_issues.rows(connection)[0]['code'])
        self.assertIn('ops_ingestion_issues', public_schema(connection)['tables'])
