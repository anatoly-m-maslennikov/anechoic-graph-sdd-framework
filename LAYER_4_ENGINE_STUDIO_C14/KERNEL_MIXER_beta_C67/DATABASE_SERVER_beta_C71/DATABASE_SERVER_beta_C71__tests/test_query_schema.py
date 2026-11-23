import unittest

import duckdb

from ..query_schema import public_schema
from ..table_names import sync_query_views


class QuerySchemaTest(unittest.TestCase):
    def setUp(self):
        self.connection = duckdb.connect()
        self.addCleanup(self.connection.close)
        self.connection.execute('CREATE TABLE mrt_atoms (reference VARCHAR, "header.state.status" VARCHAR)')
        sync_query_views(self.connection)

    def statuses(self, table):
        tables = public_schema(self.connection)["tables"]
        return next(column for column in tables[table] if column["name"] == "header.state.status").get("values", [])

    def test_family_hints_and_retained_alias(self):
        self.connection.executemany('INSERT INTO mrt_atoms VALUES (?, ?)', [
            ('AN-S-1', 'active'), ('AN-T-1', 'done'), ('AN-P-1', 'draft'), ('AN-C-1', 'active')])
        self.assertEqual(['active', 'done', 'draft'], self.statuses('atoms'))
        self.assertEqual(['active'], self.statuses('mrt_spec_atoms'))
        self.assertEqual(['done'], self.statuses('mrt_ticket_atoms'))
        self.assertEqual(['active', 'draft'], self.statuses('mrt_project_config_atoms'))
        self.connection.execute('DROP VIEW atoms')
        self.connection.execute('CREATE TABLE atoms ("header.state.status" VARCHAR)')
        self.connection.execute("INSERT INTO atoms VALUES ('legacy')")
        self.assertEqual(['legacy'], self.statuses('atoms'))

    def test_limits_are_per_family_and_measured_in_bytes(self):
        self.connection.executemany('INSERT INTO mrt_atoms VALUES (?, ?)',
                                    [(f'AN-S-{i}', str(i)) for i in range(257)] +
                                    [('AN-T-1', 'é' * 512)])
        self.assertEqual([], self.statuses('mrt_spec_atoms'))
        self.assertEqual(['é' * 512], self.statuses('mrt_ticket_atoms'))
        self.connection.execute('INSERT INTO mrt_atoms VALUES (?, ?)', ['AN-T-2', 'é' * 513])
        self.assertEqual([], self.statuses('mrt_ticket_atoms'))
        self.assertEqual([], self.statuses('mrt_atoms'))

    def test_noncanonical_family_view_keeps_own_data(self):
        self.connection.execute('DROP VIEW mrt_spec_atoms')
        self.connection.execute("CREATE VIEW mrt_spec_atoms AS SELECT * FROM mrt_atoms WHERE reference LIKE 'AN-T-%'")
        self.connection.execute("INSERT INTO mrt_atoms VALUES ('AN-T-1', 'done')")
        self.assertEqual(['done'], self.statuses('mrt_spec_atoms'))
