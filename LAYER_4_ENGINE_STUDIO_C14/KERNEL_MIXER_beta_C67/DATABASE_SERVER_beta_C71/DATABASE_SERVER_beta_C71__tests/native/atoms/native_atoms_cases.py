"""Additional native Atom tests."""

from . import test_native_atoms as origin


class NativeSchemaCases:
    def family_snapshot(self):
        native = origin._native_generation()
        source = native["snapshot"]["atoms"][0]
        for reference, status, group in (
            ("AN-S-2", "active", "Current"),
            ("AN-P-3", "active", "Current"),
            ("AN-C-4@1-draft", "draft", "Draft"),
        ):
            atom_id = reference.split("@")[0]
            native["snapshot"]["atoms"].append(
                source
                | {
                    "reference": reference,
                    "exact_ref": reference
                    if group == "Draft"
                    else f"{atom_id}@1",
                    "version": 1,
                    "status_group": group,
                    "status": status,
                    "filename": f"{atom_id}.md",
                }
            )
        native["receipt"]["snapshot_sha256"] = origin._digest(
            native["snapshot"]
        )
        return native

    def test_atom_family_views_publish_each_family_and_its_statuses(self):
        native = self.family_snapshot()
        expected = {
            "mrt_spec_atoms": ([["AN-S-2"]], ["active"]),
            "mrt_ticket_atoms": (
                [["AN-T-1"], ["AN-T-1@1"]],
                ["active", "archived"],
            ),
            "mrt_project_config_atoms": (
                [["AN-C-4@1-draft"], ["AN-P-3"]],
                ["active", "draft"],
            ),
        }
        with origin._server() as client:
            response = client.put("/generation", json=native)
            self.assertEqual(200, response.status_code, response.text)
            tables = client.get(
                "/schema", params={"instance_id": "instance"}
            ).json()["result"]["tables"]
            for table, (rows, values) in expected.items():
                with self.subTest(table=table):
                    self.assertEqual(
                        rows,
                        origin._query(
                            client, f"SELECT reference FROM {table} ORDER BY 1"
                        ).json()["result"]["rows"],
                    )
                    status = next(
                        column
                        for column in tables[table]
                        if column["name"] == "header.state.status"
                    )
                    self.assertEqual(values, status["values"])

    def test_schema_hints_follow_admitted_generation_without_query_history(
        self,
    ):
        with origin.TemporaryDirectory(dir="/tmp") as directory:
            root = origin.Path(directory).resolve()
            with origin._server(None, "--project-root", str(root)) as client:
                self.assertEqual(
                    409,
                    client.get(
                        "/schema", params={"instance_id": "instance"}
                    ).status_code,
                )
                self.assertEqual(
                    403,
                    client.get(
                        "/schema", params={"instance_id": "other"}
                    ).status_code,
                )
                native = origin._native_generation()
                self.assertEqual(
                    200, client.put("/generation", json=native).status_code
                )
                self.assert_values(client, ["active", "archived"])
                native["snapshot"]["atoms"][0]["status"] = "done"
                native["receipt"]["snapshot_sha256"] = origin._digest(
                    native["snapshot"]
                )
                self.assertEqual(
                    200, client.put("/generation", json=native).status_code
                )
                self.assert_values(client, ["archived", "done"])
                history = client.post(
                    "/workspace",
                    json={
                        "instance_id": "instance",
                        "operation": "query_log_list",
                        "arguments": {},
                    },
                )
                self.assertEqual(200, history.status_code, history.text)
                self.assertEqual([], history.json()["result"]["items"])

    def assert_values(self, client, expected):
        result = client.get("/schema", params={"instance_id": "instance"})
        self.assertEqual(200, result.status_code, result.text)
        tables = result.json()["result"]["tables"]
        self.assertIn("native_references", tables)
        self.assertNotIn("generation", tables)
        status = next(
            column
            for column in tables["atoms"]
            if column["name"] == "header.state.status"
        )
        self.assertEqual(expected, status["values"])


class StagedNativeAtomsCases:
    def test_mixed_order_empty_revisions_and_atomic_refusal(self):
        data = origin._native_generation()
        current, archived = data["snapshot"]["atoms"]
        draft = archived | {
            "reference": "AN-T-2@1-draft",
            "exact_ref": "AN-T-2@1-draft",
            "status_group": "Draft",
            "status": "draft",
            "filename": "draft.md",
        }
        data["snapshot"]["atoms"] = [
            current,
            dict(reversed(list(draft.items()))),
            archived,
        ]
        data["snapshot"]["relations"] = []
        data["receipt"]["snapshot_sha256"] = origin._digest(data["snapshot"])
        sql = (
            "SELECT stable_ref, exact_ref FROM mrt_atom_references ORDER BY "
            "reference"
        )
        expected = [
            ["AN-T-1", "AN-T-1@2"],
            [None, "AN-T-1@1"],
            [None, "AN-T-2@1-draft"],
        ]
        with origin._server() as client:
            admitted = client.put("/generation", json=data)
            self.assertEqual(200, admitted.status_code, admitted.text)
            self.assertEqual(
                expected, origin._query(client, sql).json()["result"]["rows"]
            )
            self.assert_refusal_and_empty(client, data, current, sql, expected)

    def assert_refusal_and_empty(self, client, data, current, sql, expected):
        invalid = origin.deepcopy(data)
        invalid["snapshot"]["atoms"].append(current)
        invalid["receipt"]["snapshot_sha256"] = origin._digest(
            invalid["snapshot"]
        )
        self.assertEqual(
            400, client.put("/generation", json=invalid).status_code
        )
        self.assertEqual(
            expected, origin._query(client, sql).json()["result"]["rows"]
        )
        data["snapshot"]["atoms"] = []
        data["receipt"]["snapshot_sha256"] = origin._digest(data["snapshot"])
        empty = client.put("/generation", json=data)
        self.assertEqual(200, empty.status_code, empty.text)
        self.assertEqual(
            [], origin._query(client, sql).json()["result"]["rows"]
        )
