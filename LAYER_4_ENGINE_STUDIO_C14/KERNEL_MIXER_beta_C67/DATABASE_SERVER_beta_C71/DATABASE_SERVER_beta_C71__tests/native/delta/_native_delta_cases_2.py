"""Support cases for native delta tests."""

from copy import deepcopy


from ...DATABASE_SERVER_beta_C71__tests__shared import _query, _server
from ..atoms.test_native_atoms import _digest
from .test_native_delta import base_generation, delta, edges


class DeltaCases2:
    def _create_atom(self, client):
        data = base_generation()
        base = client.put("/generation", json=data).json()["result"][
            "generation"
        ]
        original = data["snapshot"]["atoms"][0]
        created = original | {
            "reference": "AN-T-2",
            "exact_ref": "AN-T-2@1",
            "version": 1,
            "filename": "AN-T-2-TASK.md",
            "summary": "created",
        }
        key = [created["relative_path"], created["filename"]]
        base = self.send(
            client, delta(base, [key], [created], edges("AN-T-2") * 2)
        )
        self.assertEqual(
            [[2]],
            _query(
                client,
                (
                    "SELECT count(*) FROM main.relations WHERE "
                    "source_ref='AN-T-2'"
                ),
            ).json()["result"]["rows"],
        )
        self.assert_graph(client, ["AN-T-1", "AN-T-2"])
        return base, key, created

    def _move_and_delete_atom(self, client, base, key, edited):
        other = edited | {"relative_path": "moved"}
        new_key = ["moved", edited["filename"]]
        collision = client.put(
            "/generation/native-delta",
            json=delta(base, [new_key], [other], edges("AN-T-2")),
        )
        self.assertEqual(409, collision.status_code, collision.text)
        self.assertEqual(
            "delta_full_reconciliation", collision.json()["error"]["code"]
        )
        self.assertEqual(
            base, client.get("/health").json()["result"]["generation"]
        )
        base = self.send(
            client, delta(base, [key, new_key], [other], edges("AN-T-2"))
        )
        self.assertEqual(base, self.send(client, delta(base, [key], [], [])))
        self.assertEqual(
            [["moved"]],
            _query(
                client,
                "SELECT relative_path FROM atoms WHERE reference='AN-T-2'",
            ).json()["result"]["rows"],
        )
        base = self.send(client, delta(base, [new_key], [], []))
        self.assertEqual(
            [[0]],
            _query(
                client,
                "SELECT count(*) FROM atoms WHERE reference='AN-T-2'",
            ).json()["result"]["rows"],
        )
        self.assert_graph(client, ["AN-T-1"])
        self.assertEqual(
            base, client.get("/health").json()["result"]["generation"]
        )

    def test_create_edit_rename_delete_and_duplicate_collision(self):
        with _server() as client:
            base, key, created = self._create_atom(client)
            edited = created | {
                "status": "done",
                "version": 2,
                "exact_ref": "AN-T-2@2",
                "summary": "edited",
            }
            base = self.send(
                client, delta(base, [key], [edited], edges("AN-T-2"))
            )
            self.assertEqual(
                [["done", 2]],
                _query(
                    client,
                    (
                        'SELECT "header.state.status", "header.stat'
                        "e.version\" FROM atoms WHERE reference='AN-"
                        "T-2'"
                    ),
                ).json()["result"]["rows"],
            )
            self._move_and_delete_atom(client, base, key, edited)

    def _lifecycle_payload(self, client):
        data = base_generation()
        spec = data["snapshot"]["atoms"][0] | {
            "reference": "AN-S-2",
            "exact_ref": "AN-S-2@1",
            "version": 1,
            "filename": "AN-S-2-DES.md",
        }
        data["snapshot"]["atoms"].append(spec)
        data["snapshot"]["lifecycle_lenses"] = [["AN-S-2", "SPEC/TEST"]]
        data["receipt"]["snapshot_sha256"] = _digest(data["snapshot"])
        base = client.put("/generation", json=data).json()["result"][
            "generation"
        ]
        key = [spec["relative_path"], spec["filename"]]
        payload = delta(base, [key], [spec], [])
        payload["snapshot"]["lifecycle_lenses"] = [["AN-S-2", "SPEC/NEW"]]
        payload["snapshot_sha256"] = _digest(
            {"paths": payload["paths"], "snapshot": payload["snapshot"]}
        )
        bad = deepcopy(payload)
        bad["snapshot"]["lifecycle_lenses"] = [["AN-T-1", "SPEC"]]
        bad["snapshot_sha256"] = _digest(
            {"paths": bad["paths"], "snapshot": bad["snapshot"]}
        )
        return base, key, payload, bad

    def test_lifecycle_lenses_follow_delta_and_legacy_availability(self):
        with _server() as client:
            base, key, payload, bad = self._lifecycle_payload(client)
            self.assertEqual(
                400,
                client.put("/generation/native-delta", json=bad).status_code,
            )
            self.assertEqual(
                [["AN-S-2", "SPEC/TEST"]],
                _query(client, "SELECT * FROM lifecycle_lenses").json()[
                    "result"
                ]["rows"],
            )
            base = self.send(client, payload)
            self.assertEqual(
                [["AN-S-2", "SPEC/NEW"]],
                _query(client, "SELECT * FROM lifecycle_lenses").json()[
                    "result"
                ]["rows"],
            )
            base = self.send(client, delta(base, [key], [], []))
            tables = _query(
                client,
                (
                    "SELECT count(*) FROM information_schema.ta"
                    "bles WHERE table_name='lifecycle_lenses'"
                ),
            )
            self.assertEqual([[0]], tables.json()["result"]["rows"])

    def test_path_limit(self):
        with _server() as client:
            base = client.put("/generation", json=base_generation()).json()[
                "result"
            ]["generation"]
            paths = [[".", f"AN-T-{i}-TASK.md"] for i in range(1, 1026)]
            self.assertEqual(
                base, self.send(client, delta(base, paths[:1024], [], []))
            )
            response = client.put(
                "/generation/native-delta", json=delta(base, paths, [], [])
            )
            self.assertEqual(400, response.status_code, response.text)
            self.assertEqual(
                base, client.get("/health").json()["result"]["generation"]
            )
