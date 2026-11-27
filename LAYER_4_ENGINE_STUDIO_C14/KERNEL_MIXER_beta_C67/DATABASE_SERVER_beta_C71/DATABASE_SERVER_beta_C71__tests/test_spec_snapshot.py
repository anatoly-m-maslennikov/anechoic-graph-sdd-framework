import unittest

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _generation,
    _query,
    _server,
)


class SpecSnapshotTest(unittest.TestCase):
    def test_staging_binding_atomicity_and_isolation(self):
        row = {
            "source_path": "a.md",
            "exact_ref": "AN-S-1@1-draft",
            "metadata": {"nested": [1, None, "ю"]},
            "body": "text\n",
            "sha256": "b" * 64,
        }
        payload = {**BINDING, "manifest_sha256": PIN, "rows": [row]}
        with _server() as client:
            self.assertEqual(409, client.get("/spec-snapshot", params={**BINDING, "snapshot_id": "none"}).status_code)
            response = client.put("/spec-snapshot", json=payload)
            self.assertEqual(200, response.status_code, response.text)
            first = response.json()["result"]["snapshot_id"]
            params = {**BINDING, "snapshot_id": first}
            self.assertEqual({"snapshot_id": first, "rows": [row]}, client.get("/spec-snapshot", params=params).json()["result"])
            self.assertEqual(400, client.get("/spec-snapshot", params={**params, "extra": "x"}).status_code)
            self.assertEqual(400, client.put("/spec-snapshot", json={**payload, "rows": [row, {}]}).status_code)
            self.assertEqual(403, client.put("/spec-snapshot", json={**payload, "manifest_sha256": "c" * 64}).status_code)
            self.assertEqual(403, client.get("/spec-snapshot", params={**params, "instance_id": "other"}).status_code)
            self.assertEqual([row], client.get("/spec-snapshot", params=params).json()["result"]["rows"])
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            self.assertEqual(400, _query(client, "SELECT * FROM temp.main.spec_snapshot").status_code)
            second = client.put("/spec-snapshot", json={**payload, "rows": [row, row]})
            second_id = second.json()["result"]["snapshot_id"]
            self.assertEqual(
                [row, row],
                client.get(
                    "/spec-snapshot",
                    params={**BINDING, "snapshot_id": second_id},
                ).json()["result"]["rows"],
            )
            self.assertEqual(
                200,
                client.put(
                    "/spec-snapshot", json={**payload, "rows": []}
                ).status_code,
            )
            self.assertEqual(
                409, client.get("/spec-snapshot", params=params).status_code
            )
