"""Exercise partial startup and conditional Archived admission."""
import asyncio
from copy import deepcopy
import json
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import patch

import httpx2

from .. import archive_generation
from ..DATABASE_SERVER_beta_C71__shared import create_app, open_database

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    PIN,
    _query,
    _server,
)
from .test_generation_batch import _stage
from .test_native_atoms import _digest
from .test_native_refresh import graph_payload


def _partial():
    data = graph_payload()
    snapshot = data["snapshot"]
    archived = snapshot["atoms"].pop()
    data["receipt"]["snapshot_sha256"] = _digest(snapshot)
    atom = snapshot["atoms"][0]
    path = atom["relative_path"] + "/" + atom["filename"]
    data.update(archive_pending=True, carrier_hashes={path: "a" * 64})
    archive = {
        "schema_version": 2,
        "manifest_sha256": PIN,
        "atoms": [archived],
        "relations": [
            {
                "source_kind": "Atom",
                "source_ref": archived["reference"],
                "target_kind": "Component",
                "target_ref": "C00",
                "relation_type": "CONTAINED_BY",
                "derived": False,
            }
        ],
        "relation_types": snapshot["relation_types"],
    }
    path = archived["relative_path"] + "/" + archived["filename"]
    return data, archive, {path: "b" * 64}


class ArchiveGenerationTest(unittest.TestCase):
    def test_archive_batch_publishes_only_after_artifact_verification(self):
        data, archive, hashes = _partial()
        with (
            _server() as client,
            TemporaryDirectory(prefix="anechoic-archive-") as directory,
        ):
            first = client.put("/generation", json=data)
            self.assertEqual(200, first.status_code, first.text)
            base = first.json()["result"]["generation"]
            header = {
                key: [] if isinstance(value, list) else value
                for key, value in archive.items()
            }
            frames = [
                {"snapshot": header, "graph": None, "carrier_hashes": {}}
            ]
            frames.extend(
                ["snapshot", key, rows]
                for key, rows in archive.items()
                if isinstance(rows, list)
            )
            frames.append(["carrier_hashes", "", list(hashes.items())])
            descriptor = _stage(directory, frames)
            request = {**BINDING, "base_generation": base, "snapshot_sha256": _digest(archive)}
            rejected = client.put("/generation/archive", json=request | {
                "batch_artifact": descriptor | {"sha256": "a" * 64}})
            self.assertEqual(400, rejected.status_code, rejected.text)
            self.assertTrue(
                client.get("/health").json()["result"]["archive_pending"]
            )
            admitted = client.put(
                "/generation/archive",
                json=request | {"batch_artifact": descriptor},
            )
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertFalse(
                client.get("/health").json()["result"]["archive_pending"]
            )
            rows = _query(
                client,
                "SELECT exact_ref FROM mrt_atom_references ORDER BY exact_ref",
            )
            self.assertEqual(
                [["AN-T-1@1"], ["AN-T-1@2"]], rows.json()["result"]["rows"]
            )

    def test_archive_is_conditional_atomic_and_keeps_live_rows(self):
        data, archive, hashes = _partial()
        with _server() as client:
            self.assertFalse(
                client.get("/health").json()["result"]["archive_pending"]
            )
            response = client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            self.assertTrue(client.get("/health").json()["result"]["archive_pending"])
            request = {**BINDING, "base_generation": base, "snapshot": archive,
                       "snapshot_sha256": _digest(archive), "carrier_hashes": hashes}
            stale = client.put("/generation/archive", json=request | {"base_generation": "stale"})
            self.assertEqual(409, stale.status_code, stale.text)
            invalid = deepcopy(request)
            invalid["snapshot"]["atoms"][0]["relative_path"] = data[
                "snapshot"
            ]["atoms"][0]["relative_path"]
            invalid["snapshot"]["atoms"][0]["filename"] = data["snapshot"][
                "atoms"
            ][0]["filename"]
            invalid["snapshot_sha256"] = _digest(invalid["snapshot"])
            refused = client.put("/generation/archive", json=invalid)
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertTrue(client.get("/health").json()["result"]["archive_pending"])
            admitted = client.put("/generation/archive", json=request)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertNotEqual(base, admitted.json()["result"]["generation"])
            self.assertFalse(client.get("/health").json()["result"]["archive_pending"])
            rows = _query(client, (
                'SELECT stable_ref, exact_ref FROM mrt_atom_references ORDER '
                'BY exact_ref'
            ))
            self.assertEqual([[None, "AN-T-1@1"], ["AN-T-1", "AN-T-1@2"]], rows.json()["result"]["rows"])
            hashes_result = _query(client, "SELECT hashes FROM generation_carriers")
            checkpoint = json.loads(hashes_result.json()["result"]["rows"][0][0])
            self.assertEqual(2, len(checkpoint))
            findings = _query(client, "SELECT source_key, status FROM code_access_findings")
            self.assertEqual([["module:pkg/a.py", "denied"]], findings.json()["result"]["rows"])
            graph = _query(client, (
                'FROM GRAPH_TABLE (anechoic MATCH '
                '(s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s.ref '
                'AS source, t.ref AS target)) ORDER BY source'
            ))
            self.assertEqual([["AN-T-1", "C00"], ["AN-T-1@1", "C00"]], graph.json()["result"]["rows"])

    def test_preparation_allows_reads_and_rejects_stale_result(self):
        data, archive, hashes = _partial()
        entered, release = threading.Event(), threading.Event()
        original = archive_generation._prepare_archive

        def held(*args):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("preparation was not released")
            return original(*args)

        async def exercise(client):
            response = await client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            request = {**BINDING, "base_generation": base, "snapshot": archive,
                       "snapshot_sha256": _digest(archive), "carrier_hashes": hashes}
            with patch.object(archive_generation, "_prepare_archive", held):
                task = asyncio.create_task(
                    client.put("/generation/archive", json=request)
                )
                try:
                    self.assertTrue(await asyncio.to_thread(entered.wait, 2))
                    health = await asyncio.wait_for(client.get("/health"), 1)
                    self.assertTrue(health.json()["result"]["archive_pending"])
                    changed = await asyncio.wait_for(client.put("/generation/archive", json={
                        **BINDING, "base_generation": base, "unchanged": True}), 1)
                    self.assertEqual(200, changed.status_code, changed.text)
                finally:
                    release.set()
                stale = await task
            self.assertEqual(409, stale.status_code, stale.text)
            self.assertEqual(
                "generation_base_changed", stale.json()["error"]["code"]
            )
            self.assertFalse((await client.get("/health")).json()["result"]["archive_pending"])
            rows = await client.post("/database", json={**BINDING, "sql": "SELECT count(*) FROM atoms"})
            self.assertEqual([[1]], rows.json()["result"]["rows"])

        with open_database() as connection:
            app = create_app(connection, "instance", PIN)

            async def run():
                async with httpx2.AsyncClient(
                    transport=httpx2.ASGITransport(app=app),
                    base_url="http://test",
                ) as client:
                    await exercise(client)

            asyncio.run(run())

    def test_success_clears_only_archive_issues(self):
        data, archive, hashes = _partial()
        issue = {
            "relative_path": "bad.md",
            "code": "invalid",
            "message": "bad",
            "atom_ref": None,
            "related_paths": [],
        }
        with _server() as client:
            response = client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            for source in ("archive", "atom", "build"):
                reply = client.put(
                    "/ingestion/issues",
                    json={**BINDING, "source": source, "issues": [issue]},
                )
                self.assertEqual(200, reply.status_code, reply.text)
            request = {
                **BINDING,
                "base_generation": base,
                "snapshot": archive,
                "snapshot_sha256": _digest(archive),
                "carrier_hashes": hashes,
            }
            refused = client.put(
                "/generation/archive",
                json=request | {"base_generation": "stale"},
            )
            self.assertEqual(409, refused.status_code, refused.text)
            rows = client.get("/ingestion/issues", params=BINDING).json()[
                "result"
            ]["rows"]
            self.assertEqual(
                ["archive", "atom", "build"], [row["source"] for row in rows]
            )
            admitted = client.put("/generation/archive", json=request)
            self.assertEqual(200, admitted.status_code, admitted.text)
            rows = client.get("/ingestion/issues", params=BINDING).json()[
                "result"
            ]["rows"]
            self.assertEqual(
                ["atom", "build"], [row["source"] for row in rows]
            )
