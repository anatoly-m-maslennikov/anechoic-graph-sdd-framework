"""Exercise generation admission and read-only SQL through the real socket."""

from copy import deepcopy
import unittest

from .database_server_graph_cases import DatabaseServerGraphCases
from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


class DatabaseServerTest(DatabaseServerGraphCases, unittest.TestCase):
    def test_atomic_generation_and_read_only_query(self):
        with _server() as client:
            self.assertFalse(client.get("/health").json()["result"]["ready"])
            self.assertEqual(
                _query(client, "SELECT * FROM atoms").status_code, 409
            )
            self.assertEqual(
                client.get("/model", params=BINDING).status_code, 409
            )
            payload = _generation()
            generation = self.admit(client, payload)
            self.assertTrue(client.get("/health").json()["result"]["ready"])
            self.assert_equal_artifacts(client, payload, generation)
            self.assert_rollbacks(client, payload, generation)
            self.assert_read_only_query(client)
            run = _query(
                client, 'SELECT "content.summary" FROM atoms', page_size=1
            )
            query_id = run.json()["result"]["query_id"]
            payload["snapshot"]["atoms"][0]["summary"] = "second"
            next_generation = self.admit(client, payload)
            self.assertNotEqual(next_generation, generation)
            self.assert_equal_artifacts(client, payload, next_generation)
            self.assertEqual(
                [["one", "second"]],
                _query(client, "SELECT * FROM atoms").json()["result"]["rows"],
            )
            page = client.post(
                "/database",
                json={
                    **BINDING,
                    "query_id": query_id,
                    "offset": 0,
                    "page_size": 1,
                },
            )
            self.assertEqual([["first"]], page.json()["result"]["rows"])

    def admit(self, client, payload):
        response = client.put("/generation", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def assert_equal_artifacts(self, client, payload, generation):
        for name in ("model", "structure"):
            response = client.get("/" + name, params=BINDING)
            self.assertEqual(payload[name].encode(), response.content)
            self.assertEqual(
                generation, response.headers["x-anechoic-generation"]
            )

    def assert_rollbacks(self, client, payload, generation):
        duplicate = deepcopy(payload)
        duplicate["snapshot"]["atoms"] *= 2
        changed = deepcopy(payload)
        changed["receipt"]["structure_sha256"] = "c" * 64
        for invalid, status in (
            (duplicate, 400),
            (changed, 400),
            ({**payload, "instance_id": "other"}, 403),
        ):
            self.assertEqual(
                status, client.put("/generation", json=invalid).status_code
            )
            self.assert_equal_artifacts(client, payload, generation)
            self.assertEqual(
                [["one", "first"]],
                _query(client, "SELECT * FROM atoms").json()["result"]["rows"],
            )

    def assert_read_only_query(self, client):
        for sql in (
            "DELETE FROM atoms",
            "SELECT 1; SELECT 2",
            "SELECT * FROM read_csv('/etc/passwd')",
            "SELECT * FROM range(1001)",
        ):
            self.assertEqual(400, _query(client, sql).status_code)
        self.assertEqual(
            403, _query(client, "SELECT 1", instance_id="other").status_code
        )
        self.assertEqual(
            400, _query(client, "SELECT 1", extra=True).status_code
        )


if __name__ == "__main__":
    unittest.main()
