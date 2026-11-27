"""Check Current export against the generated Tool registry."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

from ...openapi import export_openapi
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    shared_tool_contract import public_tool  # fmt: skip


ENGINE = Path(__file__).resolve().parents[3]
REGISTRY = (
    ENGINE / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
    "FEATURE_IWE_CONSOLE_BACKEND/tool_registry.json"
)


class CurrentOpenApiTest(unittest.TestCase):
    def test_generated_registry_and_project_specific_tool(self):
        registry = json.loads(REGISTRY.read_text())
        document = export_openapi("test", registry)
        validate(document)
        operations = document["paths"]["/tools"]
        catalog = operations["get"]["responses"]["200"]["content"][
            "application/json"
        ]["example"]["result"]["tools"]
        names = set(registry["public_tools"])
        expected = [
            public_tool(tool)
            for provider in registry["providers"]
            for tool in provider["tools"]
            if tool["name"] in names
        ]
        self.assertEqual(expected, catalog)
        self.assertEqual(names, {tool["name"] for tool in catalog})
        self.assertTrue(all(
            "project_root" in tool["inputSchema"]["required"]
            for tool in catalog
        ))
        schema = operations["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]
        request = Draft202012Validator(schema)
        payload = {
            "name": "project_specific_tool",
            "arguments": {"project_root": "/project", "custom": 1},
            "session_id": None,
            "public_base_url": None,
        }
        request.validate(payload)
        self.assertFalse(request.is_valid(payload | {"arguments": {}}))
        self.assertFalse(request.is_valid(payload | {"arguments": None}))
        self.assertFalse(request.is_valid(
            payload | {"arguments": {"project_root": " "}}
        ))
        failure = operations["post"]["responses"]["502"]["content"][
            "application/json"
        ]["schema"]
        validator = Draft202012Validator(failure)
        validator.validate({
            "error": {
                "code": "project_receipt_mismatch",
                "message": (
                    "The API receipt does not identify the selected Project."
                ),
                "scope": "tool",
                "tool_result": {
                    "outcome": "failed",
                    "diagnostics": [
                        "project_receipt_mismatch: The API receipt does not "
                        "identify the selected Project."
                    ],
                },
            },
            "project": None,
        })
        self.assertFalse(validator.is_valid({"result": {}, "project": None}))
        self.assertEqual(
            failure,
            operations["post"]["responses"]["403"]["content"][
                "application/json"
            ]["schema"],
        )


if __name__ == "__main__":
    unittest.main()
