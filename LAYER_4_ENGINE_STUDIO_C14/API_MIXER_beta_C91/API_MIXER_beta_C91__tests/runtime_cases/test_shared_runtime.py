"""Exercise the shared API over a private peer-owner protocol fixture."""

import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from ...API_MIXER_beta_C91__shared import export_openapi
from ._shared_runtime_test_fixture import (
    EXPECTED_TOOL_NAMES,
    INSTANCE,
    SharedRuntimeFixture,
)


class SharedRuntimeTest(SharedRuntimeFixture, unittest.TestCase):
    def call(self, name="query_run", arguments=None, *, headers=None):
        return self.client.post(
            "/tools",
            json={
                "name": name,
                "arguments": arguments or {},
                "session_id": None,
                "public_base_url": None,
            },
            headers=headers,
        ).json()

    def test_explicit_selection_query_and_release(self):
        catalog = self.client.get("/tools").json()["result"]["tools"]
        self.assertEqual(
            EXPECTED_TOOL_NAMES,
            {t["name"] for t in catalog},
        )
        self.assertTrue(
            all(
                "project_root" in t["inputSchema"]["required"] for t in catalog
            )
        )
        selected = self.client.post(
            "/selection", json={"project_root": str(self.path)}
        ).json()["result"]
        self.assertEqual(
            {
                "instance_id": INSTANCE,
                "project_name": "Project",
                "project_prefix": "AN",
            },
            selected,
        )
        self.assertEqual(
            {"operation": "select", "project_root": str(self.path)},
            self.servers[0].requests[-1],
        )
        result = self.call(
            arguments={
                "project_root": str(self.path),
                "sql": "SELECT 42",
                "result_delivery": "inline",
            },
            headers={"X-Anechoic-Project-Instance": selected["instance_id"]},
        )
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        self.assertEqual(
            {"prefix": "AN", "instance_id": INSTANCE}, result["project"]
        )
        self.assertEqual([b"R"], self.servers[0].releases)
        self.assertEqual(INSTANCE, self.servers[1].requests[-1]["instance_id"])

    def test_openapi_matches_shared_http(self):
        document = export_openapi("test")
        validate(document)
        self.assertEqual(document, export_openapi("test"))
        operations = document["paths"]["/tools"]
        catalog = self.client.get("/tools").json()
        catalog_contract = operations["get"]["responses"]["200"]["content"][
            "application/json"
        ]
        Draft202012Validator(catalog_contract["schema"]).validate(catalog)
        self.assertEqual(catalog_contract["example"], catalog)

        post = operations["post"]
        schema = post["requestBody"]["content"]["application/json"]["schema"]
        request = Draft202012Validator(schema)
        self._assert_tool_catalog_schema(schema, catalog)

        call = {
            "name": "query_run",
            "arguments": {
                "project_root": str(self.path),
                "sql": "SELECT 42",
                "result_delivery": "inline",
            },
            "session_id": None,
            "public_base_url": None,
        }
        request.validate(call)
        wrong_tool = call | {"name": "query_schema"}
        self.assertFalse(request.is_valid(wrong_tool))
        self.assertFalse(request.is_valid(call | {"session_id": "  "}))
        self.assertFalse(
            request.is_valid(call | {"arguments": {"sql": "SELECT 42"}})
        )

        cases = ((call, None), (wrong_tool, "tool_input_invalid"))
        for payload, code in cases:
            response = self.client.post("/tools", json=payload)
            content = post["responses"][str(response.status_code)]["content"]
            result = response.json()
            Draft202012Validator(
                content["application/json"]["schema"]
            ).validate(result)
            if code is None:
                self.assertEqual(result["result"]["value"]["rows"], [[42]])
            else:
                self.assertEqual(result["error"]["code"], code)

    def _assert_tool_catalog_schema(self, schema, catalog):
        branches = {
            branch["properties"]["name"]["const"]: branch["properties"]
            for branch in schema["oneOf"]
        }
        self.assertEqual(len(branches), len(schema["oneOf"]))
        self.assertEqual(
            set(branches),
            {tool["name"] for tool in catalog["result"]["tools"]},
        )
        for tool in catalog["result"]["tools"]:
            advertised = deepcopy(tool["inputSchema"])
            del advertised["properties"]["caller_context"]
            advertised["properties"]["project_root"]["pattern"] = r"\S"
            self.assertEqual(branches[tool["name"]]["arguments"], advertised)

    def test_rebound_project_refuses_lifecycle_before_a_lease_or_write(self):
        owner, database, jobs = self.servers
        root = str(self.path)
        selected = self.client.post(
            "/selection", json={"project_root": root}
        ).json()["result"]
        owner.binding["instance_id"] = "c" * 64
        result = self.call(
            "atom_lifecycle_archive",
            {"project_root": root, "target": {"ref_id": "AN-S-1@1"}},
            headers={"X-Anechoic-Project-Instance": selected["instance_id"]},
        )
        self.assertEqual("project_declarations_stale", result["error"]["code"])
        self.assertNotIn("result", result)
        self.assertEqual(
            ["select", "select"],
            [
                r["operation"]
                for r in owner.requests
                if r["operation"] != "status"
            ],
        )
        self.assertEqual([], database.requests)
        self.assertEqual([], jobs.requests)

    def test_root_required_blacklist_and_binding_checks(self):
        owner = self.servers[0]
        self.assertEqual(
            "missing_project_root",
            self.call(arguments={"sql": "SELECT 1"})["error"]["code"],
        )
        self.assertEqual(
            "outside_project_root",
            self.call(arguments={"project_root": "/other", "sql": "SELECT 1"})[
                "error"
            ]["code"],
        )
        root = str(self.path)
        owner.binding["tool_blacklist"] = ["query_run"]
        self.assertEqual(
            "tool_unavailable",
            self.call(arguments={"project_root": root, "sql": "SELECT 1"})[
                "error"
            ]["code"],
        )
        for denied, called in (
            ("workbench_status", "iwe_console_status"),
            ("iwe_console_abort", "workbench_abort"),
        ):
            owner.binding["tool_blacklist"] = [denied]
            self.assertEqual(
                "tool_unavailable",
                self.call(called, {"project_root": root})["error"]["code"],
            )
        owner.binding["tool_blacklist"] = []
        self.servers[1].digest = "c" * 64
        self.assertEqual(
            "project_declarations_stale",
            self.call(arguments={"project_root": root, "sql": "SELECT 1"})[
                "error"
            ]["code"],
        )
        self.assertEqual([b"R"], owner.releases)

    def test_stale_reselection_discards_result(self):
        self.servers[0].stale = True
        response = self.call(
            arguments={"project_root": str(self.path), "sql": "SELECT 1"}
        )
        self.assertEqual(
            "project_declarations_stale", response["error"]["code"]
        )
        self.assertNotIn("result", response)
        self.assertEqual([b"R"], self.servers[0].releases)

    def test_read_only_family_and_tool_errors(self):
        root = {"project_root": str(self.path)}
        checked = self.call("query_check", {**root, "sql": "SELECT 42"})[
            "result"
        ]["value"]
        self.assertEqual((True, 1), (checked["valid"], checked["row_count"]))
        page = self.call(
            "query_page",
            {**root, "query_id": "q", "result_delivery": "inline"},
        )
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        self.assertIn(
            "atoms",
            self.call("query_schema", root)["result"]["value"]["tables"],
        )
        failure = self.call(
            "query_page", {**root, "query_id": "q", "page_size": True}
        )
        self.assertEqual("tool_input_invalid", failure["error"]["code"])
        self.assertEqual("tool", failure["error"]["scope"])
        self.assertEqual([b"R"] * 4, self.servers[0].releases)
        self.assertEqual(
            "missing_project_root", self.call("query_schema")["error"]["code"]
        )

    def test_invalid_selection_envelope_is_domain_refusal(self):
        for value in (
            [],
            {},
            {"project_root": None},
            {"project_root": 42},
            {"extra": 1},
        ):
            response = self.client.post("/selection", json=value)
            self.assertEqual(
                "invalid_project_root", response.json()["error"]["code"]
            )

    def test_lifecycle_refuses_foreign_lease_before_write(self):
        self.servers[0].lease["worker_binding"]["project_prefix"] = "OTHER"
        result = self.call(
            "atom_lifecycle_archive",
            {"project_root": str(self.path), "target": {"ref": "AN-S-1"}},
        )
        self.assertEqual("project_declarations_stale", result["error"]["code"])
        self.assertEqual([], self.servers[2].requests)
        self.assertEqual([b"R"], self.servers[0].releases)


if __name__ == "__main__":
    unittest.main()
