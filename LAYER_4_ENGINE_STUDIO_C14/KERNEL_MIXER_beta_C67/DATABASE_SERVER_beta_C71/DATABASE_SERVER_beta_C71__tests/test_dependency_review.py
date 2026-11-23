"""Exercise dependency review views through the persistent query server."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import duckdb

from ..realization_projection import prepare
from .DATABASE_SERVER_beta_C71__tests__shared import _generation, _query, _server


class DependencyReviewTest(unittest.TestCase):
    def test_stale_coupling_view_is_replaced(self):
        with duckdb.connect() as connection:
            connection.execute('CREATE TABLE old_graph (value INTEGER)')
            connection.execute('CREATE VIEW biz_package_coupling AS SELECT * FROM old_graph')
            connection.execute('DROP TABLE old_graph')
            prepare(connection)
            self.assertEqual(connection.execute('SELECT count(*) FROM mrt_diag_antipatterns').fetchone()[0], 0)

    def test_cycles_coupling_and_restart(self):
        nodes = [[p, 'package', 'python', p, 'ok', None, 'Test Package' if p == 'test' else None]
                 for p in ('a', 'b', 'c', 'solo', 'test')]
        nodes += [[m, 'module', 'python', m + '.py', 'ok', p, None]
                  for m, p in (('a1', 'a'), ('a2', 'a'), ('b1', 'b'), ('c1', 'c'), ('t1', 'test'))]
        nodes.extend([['external', 'package', 'python', None, 'ok', None, None],
                      ['module:sample.py', 'module', 'python', 'sample.py', 'ok', 'a', None]])
        occurrences = [
            ['ab1', 'a1', 'b1', 'b', 2, 3, 'internal', False], ['ab2', 'a2', 'b1', 'b', 4, 0, 'internal', False],
            ['ba', 'b1', 'a1', 'a', 5, 1, 'internal', False],
            ['bc', 'b1', 'c1', 'c', 6, 0, 'internal', False], ['at', 'a1', 't1', 't', 7, 0, 'internal', False],
            ['ta', 't1', 'a1', 'a', 8, 0, 'internal', False],
            ['external-site', 'a1', 'external', 'external', 11, 0, 'internal', False],
            ['missing', 'c1', None, 'missing', 9, 0, 'unresolved', False],
            ['within', 'a1', 'a2', 'a2', 10, 0, 'internal', False],
        ]
        data = _generation()
        data['graph'] = {'nodes': nodes, 'occurrences': occurrences, 'edges': [], 'test_edges': [], 'read_issues': [],
                         'antipattern_findings': [['sample.py', 1, 0, 'python_import_order', 'confirmed', 'late import']]}
        data['receipt']['graph_sha256'] = sha256(json.dumps(data['graph'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        with TemporaryDirectory(dir='/tmp') as directory:
            path = Path(directory).resolve() / 'db.duckdb'
            with _server(path) as client:
                response = client.put('/generation', json=data)
                self.assertEqual(response.status_code, 200, response.text)
                self.assert_views(client)
                invalid = deepcopy(data)
                invalid['graph']['antipattern_findings'][0][4] = 'unknown'
                invalid['receipt']['graph_sha256'] = sha256(json.dumps(invalid['graph'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                self.assertEqual(client.put('/generation', json=invalid).status_code, 400)
                cached = _query(client, 'SELECT * FROM antipattern_findings', page_size=20)
                self.assertEqual(cached.status_code, 200, cached.text)
                query_id = cached.json()['result']['query_id']
                for target in ('antipattern_findings', 'import_cycles', 'package_coupling'):
                    refreshed = client.put('/generation', json=data | {'refresh_target': target})
                    self.assertEqual(refreshed.status_code, 200, refreshed.text)
                    query_id = refreshed.json()['result']['result_ids'][query_id]
            with duckdb.connect(str(path)) as connection:
                connection.execute('DROP VIEW mrt_diag_antipatterns')
                connection.execute('CREATE TABLE mrt_diag_antipatterns AS FROM realization_internal.int_source_antipatterns')
                connection.execute('DROP TABLE realization_internal.int_source_antipatterns')
            with _server(path) as client:
                self.assert_views(client)
                self.assertEqual(client.put('/generation', json=_generation()).status_code, 200)
                self.assertEqual(_query(client, 'SELECT * FROM antipattern_findings').status_code, 400)

    def assert_views(self, client):
        finding = _query(client, 'SELECT relative_path, rule, status FROM antipattern_findings '
                         "WHERE rule = 'python_import_order'")
        self.assertEqual(finding.status_code, 200, finding.text)
        self.assertEqual(finding.json()['result']['rows'], [['sample.py', 'python_import_order', 'confirmed']])
        result = _query(client, "SELECT level, occurrence_key, relative_path, line, \"column\" FROM import_cycles ORDER BY 1, 2")
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['result']['rows'], [
            ['module', 'ab1', 'a1.py', 2, 3], ['module', 'ab2', 'a2.py', 4, 0],
            ['module', 'at', 'a1.py', 7, 0], ['module', 'ba', 'b1.py', 5, 1],
            ['module', 'ta', 't1.py', 8, 0], ['module', 'within', 'a1.py', 10, 0],
            ['package', 'ab1', 'a1.py', 2, 3], ['package', 'ab2', 'a2.py', 4, 0],
            ['package', 'at', 'a1.py', 7, 0], ['package', 'ba', 'b1.py', 5, 1],
            ['package', 'ta', 't1.py', 8, 0],
        ])
        result = _query(client, 'SELECT DISTINCT package_key, incoming_count, outgoing_count FROM package_coupling ORDER BY 1')
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['result']['rows'], [['a', 1, 1], ['b', 1, 2], ['c', 1, 0], ['solo', 0, 0]])
        result = _query(client, "SELECT occurrence_key FROM package_coupling WHERE package_key = 'a' AND direction = 'outgoing' ORDER BY 1")
        self.assertEqual(result.json()['result']['rows'], [['ab1'], ['ab2']])
        self.assert_antipatterns(client)

    def assert_antipatterns(self, client):
        cycle = _query(client, """SELECT split_part(detail, ' ', 1), count(*), min(status)
                                  FROM antipattern_findings WHERE rule = 'import_cycles'
                                  GROUP BY 1 ORDER BY 1""")
        self.assertEqual(cycle.status_code, 200, cycle.text)
        self.assertEqual(cycle.json()['result']['rows'], [['module', 6, 'confirmed'], ['package', 5, 'confirmed']])
        coupling = _query(client, """SELECT relative_path, line, status, detail FROM antipattern_findings
                                     WHERE rule = 'package_coupling' ORDER BY relative_path""")
        self.assertEqual(coupling.status_code, 200, coupling.text)
        self.assertEqual(coupling.json()['result']['rows'], [
            ['a', None, 'review', '1 incoming and 1 outgoing Package dependencies'],
            ['b', None, 'review', '1 incoming and 2 outgoing Package dependencies'],
            ['c', None, 'review', '1 incoming and 0 outgoing Package dependencies'],
        ])
