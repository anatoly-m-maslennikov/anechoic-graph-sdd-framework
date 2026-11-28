"""Additional native refresh tests."""

from . import test_native_refresh as source


class PendingGraphCases:
    def assert_graph_publish_rejections(self, client, payload):
        self.assertEqual(
            409,
            client.put(
                "/generation/native",
                json=payload | {"base_generation": "stale"},
            ).status_code,
        )
        self.assertEqual(
            400,
            client.put(
                "/generation/native", json=payload | {"graph_sha256": "0" * 64}
            ).status_code,
        )
        changed = payload["reuse"] | {"graph_config": {"changed": True}}
        self.assertEqual(
            409,
            client.put(
                "/generation/native", json=payload | {"reuse": changed}
            ).status_code,
        )
        bad_graph = payload["graph"] | {"test_edges": [["missing", "C00"]]}
        invalid = payload | {
            "graph": bad_graph,
            "graph_sha256": source._digest(bad_graph),
        }
        self.assertEqual(
            400, client.put("/generation/native", json=invalid).status_code
        )

    def test_pending_graph_publish_keeps_core_and_rejects_stale_base(self):
        data = source.graph_payload()
        graph = data["graph"]
        data["graph"] = None
        data["receipt"]["graph_sha256"] = source._digest(None)
        witness = {
            "inputs": {"manifest": "a" * 64, "graph": "pending"},
            "graph_config": {},
            "endpoints": source.json.loads(data["model"])["bindings"][
                "endpoints"
            ],
        }
        with source._server() as client:
            response = client.put(
                "/generation", json=data | {"reuse": witness}
            )
            self.assertEqual(200, response.status_code, response.text)
            base = response.json()["result"]["generation"]
            pending_reuse = client.get(
                "/generation/reuse", params=source.BINDING
            ).json()["result"]
            artifacts = [
                client.get(path, params=source.BINDING).content
                for path in ("/model", "/structure")
            ]
            core = source._query(client, "SELECT * FROM atoms").json()[
                "result"
            ]["rows"]
            self.assert_pending_graph(client, core)
            ready = source.deepcopy(witness)
            ready["inputs"]["graph"] = "b" * 64
            payload = source.BINDING | {
                "base_generation": base,
                "graph": graph,
                "graph_sha256": source._digest(graph),
                "reuse": ready,
            }
            self.assert_graph_publish_rejections(client, payload)
            self.assert_graph_published(client, payload, base, graph)
            self.assert_core_preserved(
                client, core, artifacts, pending_reuse, ready
            )

    def assert_core_preserved(
        self, client, core, artifacts, pending_reuse, ready
    ):
        self.assertEqual(
            core,
            source._query(client, "SELECT * FROM atoms").json()["result"][
                "rows"
            ],
        )
        self.assertEqual(
            artifacts,
            [
                client.get(path, params=source.BINDING).content
                for path in ("/model", "/structure")
            ],
        )
        self.assertEqual(
            [["uncertain"]],
            source._query(
                client, "SELECT status FROM code_access_findings"
            ).json()["result"]["rows"],
        )
        self.assertEqual(
            pending_reuse | {"inputs": ready["inputs"]},
            client.get("/generation/reuse", params=source.BINDING).json()[
                "result"
            ],
        )

    def assert_graph_published(self, client, payload, base, graph):
        published = client.put("/generation/native", json=payload)
        self.assertEqual(200, published.status_code, published.text)
        self.assertEqual(base, published.json()["result"]["generation"])
        self.assertEqual(
            409, client.put("/generation/native", json=payload).status_code
        )
        self.assertEqual(
            400,
            client.put(
                "/generation/native", json=payload | {"force_graph": False}
            ).status_code,
        )
        self.assertEqual(
            409,
            client.put(
                "/generation/native",
                json=payload
                | {"force_graph": True, "base_generation": "stale"},
            ).status_code,
        )
        refreshed_graph = source.deepcopy(graph)
        refreshed_graph["code_access_findings"][0][5] = "uncertain"
        forced = client.put(
            "/generation/native",
            json=payload
            | {
                "force_graph": True,
                "graph": refreshed_graph,
                "graph_sha256": source._digest(refreshed_graph),
            },
        )
        self.assertEqual(200, forced.status_code, forced.text)

    def assert_pending_graph(self, client, core):
        joined = source._query(
            client,
            (
                "SELECT count(*) FROM atoms JOIN native_references USING "
                "(reference)"
            ),
        )
        self.assertEqual([[len(core)]], joined.json()["result"]["rows"])
        native = source._query(
            client,
            (
                "FROM GRAPH_TABLE (anechoic MATCH "
                "(s:Reference)-[e:CONTAINED_BY]->(t:Reference) COLUMNS (s."
                "ref AS source))"
            ),
        )
        self.assertEqual(200, native.status_code, native.text)
        self.assertEqual(
            200, client.get("/schema", params=source.BINDING).status_code
        )
        pending = source._query(client, "SELECT * FROM code_access_findings")
        self.assertEqual(
            (409, "project_graph_pending"),
            (pending.status_code, pending.json()["error"]["code"]),
        )
        joined_pending = source._query(
            client,
            (
                "SELECT count(*) FROM code_access_findings JOIN (SELECT "
                "node_key AS source_key FROM import_nodes) USING (source_key)"
            ),
        )
        self.assertEqual(
            (409, "project_graph_pending"),
            (
                joined_pending.status_code,
                joined_pending.json()["error"]["code"],
            ),
        )

    def test_warm_graph_publish_and_disabled_rejection(self):
        data = source.graph_payload()
        witness = {
            "inputs": {"manifest": "a" * 64, "graph": "b" * 64},
            "graph_config": {},
            "endpoints": source.json.loads(data["model"])["bindings"][
                "endpoints"
            ],
        }
        with source._server() as client:
            admitted = client.put(
                "/generation", json=data | {"reuse": witness}
            )
            self.assertEqual(200, admitted.status_code, admitted.text)
            base = admitted.json()["result"]["generation"]
            ready = source.deepcopy(witness)
            ready["inputs"]["graph"] = "c" * 64
            graph = source.deepcopy(data["graph"])
            graph["code_access_findings"][0][5] = "uncertain"
            payload = source.BINDING | {
                "base_generation": base,
                "graph": graph,
                "graph_sha256": source._digest(graph),
                "reuse": ready,
            }
            self.assertEqual(
                409,
                client.put(
                    "/generation/native",
                    json=payload | {"base_generation": "stale"},
                ).status_code,
            )
            updated = client.put("/generation/native", json=payload)
            self.assertEqual(200, updated.status_code, updated.text)
            self.assertEqual(base, updated.json()["result"]["generation"])
            self.assertEqual(
                [["uncertain"]],
                source._query(
                    client, "SELECT status FROM code_access_findings"
                ).json()["result"]["rows"],
            )
            self.assertEqual(
                409, client.put("/generation/native", json=payload).status_code
            )
            self.assert_disabled_graph(client, witness, data, payload)

    def assert_disabled_graph(self, client, witness, data, payload):
        disabled = source.deepcopy(witness)
        disabled["inputs"]["graph"] = "disabled"
        admitted = client.put("/generation", json=data | {"reuse": disabled})
        self.assertEqual(200, admitted.status_code, admitted.text)
        refused = client.put(
            "/generation/native",
            json=payload
            | {"base_generation": admitted.json()["result"]["generation"]},
        )
        self.assertEqual(409, refused.status_code)
        self.assertEqual(
            [["denied"]],
            source._query(
                client, "SELECT status FROM code_access_findings"
            ).json()["result"]["rows"],
        )
