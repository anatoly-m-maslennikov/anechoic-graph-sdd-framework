import unittest

import duckdb
from starlette.testclient import TestClient

from ....DATABASE_SERVER_beta_C71__shared import create_app


class QuerySchemaTest(unittest.TestCase):
    def setUp(self):
        self.connection = duckdb.connect()
        self.addCleanup(self.connection.close)
        self.connection.execute(
            (
                "CREATE TABLE mrt_atoms (reference VARCHAR, "
                '"header.state.status" VARCHAR)'
            )
        )
        self.connection.execute("CREATE TABLE ops_generation (id VARCHAR)")
        self.connection.execute(
            "INSERT INTO ops_generation VALUES ('generation')"
        )
        for name, families in (
            ("mrt_spec_atoms", "'S'"),
            ("mrt_ticket_atoms", "'T'"),
            ("mrt_project_config_atoms", "'P', 'C'"),
        ):
            self.connection.execute(
                f"CREATE VIEW {name} AS SELECT * FROM mrt_atoms "
                f"WHERE split_part(reference, '-', 2) IN ({families})"
            )
        self.connection.execute("CREATE VIEW atoms AS SELECT * FROM mrt_atoms")
        self.client = self.enterContext(
            TestClient(create_app(self.connection, "instance", "a" * 64))
        )

    def statuses(self, table):
        response = self.client.get(
            "/schema", params={"instance_id": "instance"}
        )
        self.assertEqual(200, response.status_code, response.text)
        tables = response.json()["result"]["tables"]
        return next(
            column
            for column in tables[table]
            if column["name"] == "header.state.status"
        ).get("values", [])

    def test_family_hints_and_retained_alias(self):
        self.connection.executemany(
            "INSERT INTO mrt_atoms VALUES (?, ?)",
            [
                ("AN-S-1", "active"),
                ("AN-T-1", "done"),
                ("AN-P-1", "draft"),
                ("AN-C-1", "active"),
            ],
        )
        self.assertEqual(["active", "done", "draft"], self.statuses("atoms"))
        self.assertEqual(["active"], self.statuses("mrt_spec_atoms"))
        self.assertEqual(["done"], self.statuses("mrt_ticket_atoms"))
        self.assertEqual(
            ["active", "draft"], self.statuses("mrt_project_config_atoms")
        )
        self.connection.execute("DROP VIEW atoms")
        self.connection.execute(
            'CREATE TABLE atoms ("header.state.status" VARCHAR)'
        )
        self.connection.execute("INSERT INTO atoms VALUES ('legacy')")
        self.assertEqual(["legacy"], self.statuses("atoms"))

    def test_limits_are_per_family_and_measured_in_bytes(self):
        self.connection.executemany(
            "INSERT INTO mrt_atoms VALUES (?, ?)",
            [(f"AN-S-{i}", str(i)) for i in range(257)]
            + [("AN-T-1", "é" * 512)],
        )
        self.assertEqual([], self.statuses("mrt_spec_atoms"))
        self.assertEqual(["é" * 512], self.statuses("mrt_ticket_atoms"))
        self.connection.execute(
            "INSERT INTO mrt_atoms VALUES (?, ?)", ["AN-T-2", "é" * 513]
        )
        self.assertEqual([], self.statuses("mrt_ticket_atoms"))
        self.assertEqual([], self.statuses("mrt_atoms"))

    def test_noncanonical_family_view_keeps_own_data(self):
        self.connection.execute("DROP VIEW mrt_spec_atoms")
        self.connection.execute(
            (
                "CREATE VIEW mrt_spec_atoms AS SELECT * FROM mrt_atoms WHERE "
                "reference LIKE 'AN-T-%'"
            )
        )
        self.connection.execute(
            "INSERT INTO mrt_atoms VALUES ('AN-T-1', 'done')"
        )
        self.assertEqual(["done"], self.statuses("mrt_spec_atoms"))

    def test_database_request_shapes_and_strict_types(self):
        bare = {"instance_id": "instance", "sql": "SELECT 42"}
        run = bare | {"page_size": 1}
        result = self.client.post("/database", json=bare).json()["result"]
        self.assertEqual({"columns", "rows"}, set(result))
        self.assertEqual([[42]], result["rows"])
        response = self.client.post(
            "/database",
            json=run | {"preview": None, "grid": None, "save": False},
        )
        self.assertEqual(200, response.status_code, response.text)
        query_id = response.json()["result"]["query_id"]
        page = {
            "instance_id": "instance",
            "query_id": query_id,
            "offset": 0,
            "page_size": 1,
        }
        response = self.client.post("/database", json=page | {"preview": 0})
        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual([], response.json()["result"]["rows"])
        for body, message in (
            (bare | {"preview": None}, "Invalid request fields"),
            (page | {"save": False}, "Invalid request fields"),
            (page | {"sql": bare["sql"]}, "Invalid request fields"),
            (run | {"name": None}, "name is only supported when save is true"),
            (run | {"save": True, "name": None}, "name must be a string"),
            (
                run | {"page_size": True},
                "page_size must be an integer from 1 to 1000",
            ),
            (run | {"preview": "2"}, "preview must be a non-negative integer"),
            (
                page | {"offset": False},
                "offset must be a non-negative integer",
            ),
            (page | {"query_id": 1}, "Unknown query_id"),
        ):
            with self.subTest(body=body):
                self.assert_database_error(
                    self.client, body, 400, "invalid_query", message
                )

    def assert_database_error(self, client, body, status, code, message):
        response = client.post("/database", json=body)
        self.assertEqual(status, response.status_code, response.text)
        self.assertEqual(
            {"error": {"code": code, "message": message}}, response.json()
        )

    def assert_pre_generation_precedence(self, app, run, page):
        with TestClient(app) as client:
            for body, status, code, message in (
                (
                    run | {"instance_id": None, "extra": True},
                    400,
                    "invalid_query",
                    "Invalid request fields",
                ),
                (
                    run | {"instance_id": None, "save": "true"},
                    403,
                    "foreign_instance",
                    "Instance does not match",
                ),
                (
                    run | {"save": 1, "name": None},
                    400,
                    "invalid_query",
                    "save must be a boolean",
                ),
                (
                    run,
                    409,
                    "generation_required",
                    "Generation admission required",
                ),
            ):
                with self.subTest(body=body):
                    self.assert_database_error(
                        client, body, status, code, message
                    )
            self.assert_journal_precedence(client, run, page)

    def assert_journal_precedence(self, client, run, page):
        self.connection.execute(
            "INSERT INTO ops_generation VALUES ('generation')"
        )
        self.assert_database_error(
            client,
            run,
            409,
            "journal_unavailable",
            "Work Journal is unavailable",
        )
        self.assert_database_error(
            client,
            page,
            400,
            "invalid_query",
            "offset must be a non-negative integer",
        )

    def test_database_request_checks_keep_precedence(self):
        def unavailable():
            raise OSError("unavailable")

        self.connection.execute("DELETE FROM ops_generation")
        app = create_app(
            self.connection, "instance", "a" * 64, journal_sync=unavailable
        )
        run = {
            "instance_id": "instance",
            "sql": 17,
            "page_size": False,
            "result_delivery": "bad",
        }
        page = {
            "instance_id": "instance",
            "query_id": 17,
            "offset": False,
            "page_size": 1,
        }
        self.assert_pre_generation_precedence(app, run, page)
        self.assert_database_error(
            self.client,
            run,
            400,
            "invalid_query",
            "page_size must be an integer from 1 to 1000",
        )
        self.assert_database_error(
            self.client,
            run | {"page_size": 1, "preview": False},
            400,
            "invalid_query",
            "result_delivery must be file, inline or auto",
        )
        bad_format = []
        with self.assertRaises(TypeError) as failed:
            self.assertIn(bad_format, {"json_matrix": "json"})
        request = run | {
            "page_size": 1,
            "result_delivery": "inline",
            "result_format": bad_format,
        }
        self.assert_database_error(
            self.client, request, 400, "invalid_query", str(failed.exception)
        )
