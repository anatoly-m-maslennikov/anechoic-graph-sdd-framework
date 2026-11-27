import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)
from .test_native_atoms import _digest


class IngestionIssuesTest(unittest.TestCase):
    def test_build_diagnostics_before_and_after_admission(self):
        diagnostic = {
            "attempt_id": "try",
            "accepted_generation": "untrusted",
            "severity": "ERROR",
            "code": "invalid",
            "message": "bad Model",
            "atom_ref": None,
            "source_path": None,
            "subject": None,
        }
        payload = {
            **BINDING,
            "source": "build",
            "issues": [],
            "model_diagnostics": [diagnostic],
        }
        with _server() as client:
            response = client.put("/ingestion/issues", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                200, client.put("/generation", json=_generation()).status_code
            )
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

    def test_source_read_issues_follow_realization_scan(self):
        data = _generation()
        data["graph"] = {
            "nodes": [],
            "occurrences": [],
            "edges": [],
            "test_edges": [],
            "read_issues": [["bad.py", "unreadable"]],
        }
        with _server() as client:
            data["receipt"]["graph_sha256"] = _digest(data["graph"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            result = _query(
                client,
                "SELECT source, relative_path, code, message FROM main.ops_ingestion_issues",
            )
            self.assertEqual(
                [["realization", "bad.py", "read_error", "unreadable"]],
                result.json()["result"]["rows"],
            )
            result = _query(client, "SELECT * FROM main.import_read_issues")
            self.assertEqual(
                [["bad.py", "unreadable"]], result.json()["result"]["rows"]
            )
            data["graph"]["read_issues"] = []
            data["receipt"]["graph_sha256"] = _digest(data["graph"])
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertEqual(
                [],
                client.get("/ingestion/issues", params=BINDING).json()[
                    "result"
                ]["rows"],
            )

    def test_route_before_generation_and_source_replacement(self):
        issue = {
            "relative_path": "a.md",
            "code": "invalid",
            "message": "bad",
            "atom_ref": None,
            "related_paths": [],
        }
        build_issue = {**issue, "relative_path": None}
        with _server() as client:
            self.assertEqual([], client.get('/ingestion/issues', params=BINDING).json()['result']['rows'])
            for source, row in (('atom', issue), ('build', build_issue)):
                response = client.put('/ingestion/issues', json={**BINDING, 'source': source, 'issues': [row]})
                self.assertEqual(200, response.status_code, response.text)
                self.assertEqual({'source': source, 'count': 1}, response.json()['result'])
            replacement = {**issue, 'relative_path': 'replacement.md'}
            for bad in ({'code': 'missing_fields'}, {**issue, 'extra': True}, {**issue, 'related_paths': 'invalid'},
                        {**issue, 'related_paths': [True]}, {**issue, 'message': ''}):
                payload = {**BINDING, 'source': 'atom', 'issues': [replacement, bad]}
                response = client.put('/ingestion/issues', json=payload)
                self.assertEqual(400, response.status_code, response.text)
                self.assertEqual({'code': 'invalid_ingestion_issues', 'message': 'Invalid ingestion issue'},
                                 response.json()['error'])
            bad_batch = {**BINDING, 'source': 'atom', 'issues': issue}
            response = client.put('/ingestion/issues', json=bad_batch)
            self.assertEqual(400, response.status_code, response.text)
            self.assertEqual(
                "Invalid ingestion issue source or rows",
                response.json()["error"]["message"],
            )
            response = client.put(
                "/ingestion/issues",
                json={**bad_batch, "instance_id": "foreign"},
            )
            self.assertEqual(403, response.status_code, response.text)
            self.assertEqual(403, client.get('/ingestion/issues', params={'instance_id': 'foreign'}).status_code)
            rows = client.get('/ingestion/issues', params=BINDING).json()['result']['rows']
            self.assertEqual([{'source': 'atom', **issue}, {'source': 'build', **build_issue}], rows)
            self.assertEqual(200, client.put('/ingestion/issues', json={**BINDING, 'source': 'atom', 'issues': []}).status_code)
            self.assertEqual(['build'], [row['source'] for row in client.get('/ingestion/issues', params=BINDING).json()['result']['rows']])
            self.assertEqual(200, client.put('/generation', json=_generation()).status_code)
            self.assertIn('ops_ingestion_issues', client.get('/schema', params=BINDING).json()['result']['tables'])
            self.assertEqual([], _query(client, 'SELECT source, relative_path FROM main.ops_ingestion_issues').json()['result']['rows'])
            self.assertEqual(400, _query(client, 'DELETE FROM main.ops_ingestion_issues').status_code)

    def test_legacy_migration_and_public_schema(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db.duckdb"
            with _server(path):
                pass
            with duckdb.connect(str(path)) as connection:
                connection.execute(
                    "CREATE TABLE mrt_diag_import_read_issues (relative_path VARCHAR PRIMARY KEY, error_message VARCHAR NOT NULL)"
                )
                connection.execute(
                    "INSERT INTO mrt_diag_import_read_issues VALUES ('bad.py', 'unreadable')"
                )
                connection.execute(
                    "CREATE VIEW import_read_issues AS SELECT * FROM mrt_diag_import_read_issues"
                )
                connection.execute(
                    "CREATE VIEW mrt_import_read_issues AS SELECT * FROM mrt_diag_import_read_issues"
                )
            with _server(path) as client:
                issues = client.get(
                    "/ingestion/issues", params=BINDING
                ).json()["result"]["rows"]
                self.assertEqual(1, len(issues))
                self.assertEqual("read_error", issues[0]["code"])
                self.assertEqual(
                    ("bad.py", "unreadable"),
                    (issues[0]["relative_path"], issues[0]["message"]),
                )
                self.assertEqual(
                    200,
                    client.put("/generation", json=_generation()).status_code,
                )
                self.assertIn(
                    "ops_ingestion_issues",
                    client.get("/schema", params=BINDING).json()["result"][
                        "tables"
                    ],
                )
