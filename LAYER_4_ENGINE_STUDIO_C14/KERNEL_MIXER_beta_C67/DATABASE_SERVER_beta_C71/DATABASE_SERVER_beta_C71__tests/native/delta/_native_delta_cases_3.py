"""Support cases for native delta tests."""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import duckdb
import httpx2

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _query,
    _server,
)
from .test_native_delta import base_generation, delta, edges
from ....DATABASE_SERVER_beta_C71__shared import create_app


class DeltaCases3:
    def _bulk_payload(self, client):
        data = base_generation()
        base = client.put("/generation", json=data).json()["result"][
            "generation"
        ]
        original = data["snapshot"]["atoms"][0]
        atoms = [
            original
            | {
                "reference": f"AN-T-{i}",
                "exact_ref": f"AN-T-{i}@1",
                "version": 1,
                "filename": f"AN-T-{i}-TASK.md",
                "summary": f"ticket {i}",
            }
            for i in range(2, 502)
        ]
        paths = [[a["relative_path"], a["filename"]] for a in atoms]
        relations = [
            edge for atom in atoms for edge in edges(atom["reference"])
        ]
        payload = delta(base, paths, atoms, relations)
        new_base = self.send(client, payload)
        return new_base, paths, payload

    @staticmethod
    def _accepted_state(client):
        return (
            client.get("/health").json()["result"]["generation"],
            [
                client.get(path, params=BINDING).content
                for path in ("/model", "/structure")
            ],
            [
                _query(client, sql).json()["result"]["rows"]
                for sql in (
                    "SELECT * FROM atoms ORDER BY ALL",
                    "SELECT * FROM main.relations ORDER BY ALL LIMIT 1000",
                    (
                        "SELECT * FROM main.relations ORDER BY ALL "
                        "LIMIT 1000 OFFSET 1000"
                    ),
                )
            ],
        )

    def test_bulk_500_rows_and_stale_base(self):
        with _server() as client:
            new_base, paths, payload = self._bulk_payload(client)

            before = self._accepted_state(client)
            refused = client.put("/generation/native-delta", json=payload)
            self.assertEqual(
                (409, "generation_base_changed"),
                (refused.status_code, refused.json()["error"]["code"]),
            )
            self.assertEqual(before, self._accepted_state(client))
            self.assertEqual(
                [[1002]],
                _query(client, "SELECT count(*) FROM main.relations").json()[
                    "result"
                ]["rows"],
            )
            sql = _query(
                client, "SELECT count(*), count(DISTINCT reference) FROM atoms"
            )
            self.assertEqual([[502, 502]], sql.json()["result"]["rows"])
            graph = _query(
                client,
                (
                    "FROM GRAPH_TABLE (anechoic MATCH (s:Refere"
                    "nce)-[e:CONTAINED_BY]->(t:Reference) COLUM"
                    "NS (s.ref AS source)) SELECT count(*)"
                ),
            )
            self.assertEqual([[501]], graph.json()["result"]["rows"])
            self.send(client, delta(new_base, paths, [], []))
            self.assertEqual(
                [[2]],
                _query(client, "SELECT count(*) FROM atoms").json()["result"][
                    "rows"
                ],
            )
            self.assert_graph(client, ["AN-T-1"])

    async def _exercise_rollback(
        self, app, route, base, key, atom, connection
    ):
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            with patch.dict(
                route.endpoint.__globals__,
                {
                    "_write_graph": unittest.mock.Mock(
                        side_effect=duckdb.Error("injected failure")
                    )
                },
            ):
                response = await client.put(
                    "/generation/native-delta",
                    json=delta(base, [key], [], []),
                )
            self.assertEqual(400, response.status_code, response.text)
            self.assertEqual(
                base,
                connection.execute("SELECT id FROM generation").fetchone()[0],
            )
            self.assertEqual(
                2,
                connection.execute("SELECT count(*) FROM atoms").fetchone()[0],
            )
            self.assertEqual(
                2,
                connection.execute(
                    "SELECT count(*) FROM relations"
                ).fetchone()[0],
            )
            response = await client.put(
                "/generation/native-delta",
                json=delta(base, [key], [atom], edges("AN-T-1")),
            )
            self.assertEqual(200, response.status_code, response.text)

    def test_failed_write_rolls_back(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db.duckdb"
            data = base_generation()
            with _server(path) as client:
                base = client.put("/generation", json=data).json()["result"][
                    "generation"
                ]
            atom = data["snapshot"]["atoms"][0]
            key = [atom["relative_path"], atom["filename"]]
            with duckdb.connect(str(path)) as connection:
                app = create_app(connection, BINDING["instance_id"], PIN)
                route = next(
                    r
                    for r in app.routes
                    if r.path == "/generation/native-delta"
                )

                asyncio.run(
                    self._exercise_rollback(
                        app, route, base, key, atom, connection
                    )
                )

    def test_native_carrier_families_add_update_remove(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"][
                "generation"
            ]
            original = data["snapshot"]["atoms"][0]
            for family in "SPC":
                ref = f"AN-{family}-2"
                atom = original | {
                    "reference": ref,
                    "exact_ref": f"{ref}@1",
                    "version": 1,
                    "filename": f"{ref}-DES.md",
                    "status": "active",
                }
                key = [atom["relative_path"], atom["filename"]]
                base = self.send(
                    client, delta(base, [key], [atom], edges(ref))
                )
                edited = atom | {
                    "version": 2,
                    "exact_ref": f"{ref}@2",
                    "summary": "edited",
                }
                base = self.send(
                    client, delta(base, [key], [edited], edges(ref))
                )
                rows = _query(
                    client,
                    f'SELECT "header.state.version" FROM atoms '
                    f"WHERE reference='{ref}'",
                )
                self.assertEqual([[2]], rows.json()["result"]["rows"])
                base = self.send(client, delta(base, [key], [], []))
                rows = _query(
                    client,
                    f"SELECT count(*) FROM atoms WHERE reference='{ref}'",
                )
                self.assertEqual([[0]], rows.json()["result"]["rows"])
            self.assert_graph(client, ["AN-T-1"])

    def test_native_path_rejects_mismatched_identity_and_revision(self):
        with _server() as client:
            data = base_generation()
            base = client.put("/generation", json=data).json()["result"][
                "generation"
            ]
            original = data["snapshot"]["atoms"][0]
            for filename in (
                "AN-P-3-DES.md",
                "AN-S-2@2-DES.md",
                "AN-X-2-DES.md",
            ):
                atom = original | {
                    "reference": "AN-S-2",
                    "exact_ref": "AN-S-2@1",
                    "version": 1,
                    "filename": filename,
                    "status": "active",
                }
                key = [atom["relative_path"], filename]
                response = client.put(
                    "/generation/native-delta",
                    json=delta(base, [key], [atom], []),
                )
                self.assertEqual(400, response.status_code, response.text)
                self.assertEqual(
                    base, client.get("/health").json()["result"]["generation"]
                )
