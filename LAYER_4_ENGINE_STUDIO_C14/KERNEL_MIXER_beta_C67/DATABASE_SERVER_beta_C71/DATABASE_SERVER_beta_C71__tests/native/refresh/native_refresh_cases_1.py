"""Additional native refresh tests."""

from . import test_native_refresh as source

STATUS_DOMAINS = {
    "S": ["active", "archived", "draft", "ready"],
    "T": [
        "active",
        "archived",
        "backlog",
        "canceled",
        "complete",
        "done",
        "draft",
        "in_queue",
        "resolved",
    ],
    "P": ["active", "archived", "draft"],
    "C": ["active", "archived", "draft"],
}


class NativeRefreshCases:
    def test_reuse_witness_persists_and_tracks_native_generation(self):
        with source.TemporaryDirectory(dir="/tmp") as directory:
            database = source.Path(directory).resolve() / "projection.duckdb"
            data = source.graph_payload()
            endpoints = source.json.loads(data["model"])["bindings"][
                "endpoints"
            ]
            witness = {
                "inputs": {"manifest": "a" * 64, "graph": "b" * 64},
                "graph_config": {},
                "endpoints": endpoints,
            }
            base = self.assert_initial_reuse(database, data, witness)
            self.assert_reuse_reopen(database, base, witness, data)

    def assert_initial_reuse(self, database, data, witness):
        expected = {**witness, "status_domains": STATUS_DOMAINS}
        with source._server(database) as client:
            self.assertIsNone(
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ]
            )
            self.assertEqual(
                403,
                client.get(
                    "/generation/reuse", params={"instance_id": "other"}
                ).status_code,
            )
            accepted = client.put(
                "/generation", json=data | {"reuse": witness}
            )
            self.assertEqual(200, accepted.status_code, accepted.text)
            base = accepted.json()["result"]["generation"]
            bad = source.deepcopy(witness)
            bad["endpoints"] = {}
            refused = client.put("/generation", json=data | {"reuse": bad})
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertEqual(
                {"base_generation": base, **expected},
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ],
            )
            ordinary = client.put(
                "/generation/native",
                json=source.request(base, data["snapshot"]),
            )
            self.assertEqual(200, ordinary.status_code, ordinary.text)
            base = ordinary.json()["result"]["generation"]
            self.assertEqual(
                {"base_generation": base, **expected},
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ],
            )
        return base

    def assert_reuse_reopen(self, database, base, witness, data):
        expected = {**witness, "status_domains": STATUS_DOMAINS}
        with source._server(database) as client:
            self.assertEqual(
                {"base_generation": base, **expected},
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ],
            )
            payload = source.request(base, data["snapshot"]) | {
                "graph": data["graph"],
                "graph_sha256": source._digest(data["graph"]),
            }
            witness["inputs"]["graph"] = "c" * 64
            updated = client.put(
                "/generation/native", json=payload | {"reuse": witness}
            )
            self.assertEqual(200, updated.status_code, updated.text)
            base = updated.json()["result"]["generation"]
            self.assertEqual(
                {"base_generation": base, **expected},
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ],
            )
            cleared = client.put(
                "/generation/native",
                json=payload | {"base_generation": base},
            )
            self.assertEqual(200, cleared.status_code, cleared.text)
            self.assertIsNone(
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ]
            )

    def test_carrier_checkpoint_restart_deletion_and_invalidation(self):
        with source.TemporaryDirectory(dir="/tmp") as directory:
            database = source.Path(directory).resolve() / "projection.duckdb"
            data = source.graph_payload()
            endpoints = source.json.loads(data["model"])["bindings"][
                "endpoints"
            ]
            witness = {
                "inputs": {"manifest": "a" * 64, "graph": "b" * 64},
                "graph_config": {},
                "endpoints": endpoints,
            }
            atoms = data["snapshot"]["atoms"]
            hashes = {
                f"{a['relative_path']}/{a['filename']}": "c" * 64
                for a in atoms
            }
            with source._server(database) as client:
                bad = client.put(
                    "/generation",
                    json=data | {"reuse": witness, "carrier_hashes": {}},
                )
                self.assertEqual(400, bad.status_code, bad.text)
                admitted = client.put(
                    "/generation",
                    json=data | {"reuse": witness, "carrier_hashes": hashes},
                )
                self.assertEqual(200, admitted.status_code, admitted.text)
                base = admitted.json()["result"]["generation"]
            self.assert_checkpoint_reopen(database, hashes, atoms, data, base)

    def assert_checkpoint_reopen(self, database, hashes, atoms, data, base):
        with source._server(database) as client:
            self.assertEqual(
                hashes,
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ]["carrier_hashes"],
            )
            archived = atoms[1]
            paths = [[archived["relative_path"], archived["filename"]]]
            snapshot = data["snapshot"] | {"atoms": [], "relations": []}
            delta = {
                "paths": paths,
                "snapshot": snapshot,
                "carrier_hashes": {},
            }
            payload = source.BINDING | {
                "base_generation": base,
                **delta,
                "snapshot_sha256": source._digest(delta),
            }
            refused = client.put(
                "/generation/native-delta",
                json=payload | {"snapshot_sha256": "0" * 64},
            )
            self.assertEqual(400, refused.status_code, refused.text)
            self.assertEqual(
                hashes,
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ]["carrier_hashes"],
            )
            deleted = client.put("/generation/native-delta", json=payload)
            self.assertEqual(200, deleted.status_code, deleted.text)
            base = deleted.json()["result"]["generation"]
            del hashes[f"{archived['relative_path']}/{archived['filename']}"]
            self.assertEqual(
                hashes,
                client.get("/generation/reuse", params=source.BINDING).json()[
                    "result"
                ]["carrier_hashes"],
            )
            self.assert_legacy_delta(client, paths, snapshot, base)

    def assert_legacy_delta(self, client, paths, snapshot, base):
        old = {"paths": paths, "snapshot": snapshot}
        legacy = client.put(
            "/generation/native-delta",
            json=source.BINDING
            | {
                "base_generation": base,
                **old,
                "snapshot_sha256": source._digest(old),
            },
        )
        self.assertEqual(200, legacy.status_code, legacy.text)
        self.assertNotIn(
            "carrier_hashes",
            client.get("/generation/reuse", params=source.BINDING).json()[
                "result"
            ],
        )

    def test_reuse_proof_includes_persisted_pending_archive(self):
        with source.TemporaryDirectory(dir="/tmp") as directory:
            database = source.Path(directory).resolve() / "projection.duckdb"
            data = source.graph_payload()
            snapshot = data["snapshot"]
            snapshot["atoms"].pop()
            data["receipt"]["snapshot_sha256"] = source._digest(snapshot)
            atom = snapshot["atoms"][0]
            hashes = {f"{atom['relative_path']}/{atom['filename']}": "c" * 64}
            witness = {
                "inputs": {"manifest": "a" * 64, "graph": "b" * 64},
                "graph_config": {},
                "endpoints": source.json.loads(data["model"])["bindings"][
                    "endpoints"
                ],
            }
            data.update(reuse=witness, carrier_hashes=hashes)
            with source._server(database) as client:
                response = client.put(
                    "/generation", json=data | {"archive_pending": True}
                )
                self.assertEqual(200, response.status_code, response.text)
                base = response.json()["result"]["generation"]
            self.assert_archive_proof(database, base, witness, hashes, data)

    def assert_archive_proof(self, database, base, witness, hashes, data):
        with source._server(database) as client:
            proof = client.get(
                "/generation/reuse", params=source.BINDING
            ).json()["result"]
            self.assertEqual(
                {
                    "base_generation": base,
                    **witness,
                    "status_domains": STATUS_DOMAINS,
                    "carrier_hashes": hashes,
                    "archive_pending": True,
                },
                proof,
            )
            response = client.put("/generation", json=data)
            self.assertEqual(200, response.status_code, response.text)
            proof = client.get(
                "/generation/reuse", params=source.BINDING
            ).json()["result"]
            self.assertEqual(
                {
                    "base_generation": response.json()["result"]["generation"],
                    **witness,
                    "status_domains": STATUS_DOMAINS,
                    "carrier_hashes": hashes,
                },
                proof,
            )
