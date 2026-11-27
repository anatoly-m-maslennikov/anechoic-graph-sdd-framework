"""Check the shared beta Backend contract at the MCP consumer boundary."""

from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator
from mcp import types

from API_MIXER_beta_C91.api import descriptors
from API_MIXER_beta_C91.openapi import export_openapi
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import take_caller_context
from API_MIXER_beta_C91._shared_runtime_support import TOOL_REST_PATH
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend import (
    SharedGatewayRefusal,
    _raise_fault,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import (
    valid_tool_response,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_tool_contract import public_tool


def _response_contract(operation, status):
    return operation["responses"][status]["content"]["application/json"]


class SharedBetaContractTest(unittest.TestCase):
    def setUp(self):
        paths = export_openapi("test")["paths"]
        self.assertEqual({"/tools"}, set(paths))
        self.operations = paths[TOOL_REST_PATH]
        self.post = self.operations["post"]
        self.request_body = self.post["requestBody"]
        self.request_schema = self.request_body["content"]["application/json"][
            "schema"
        ]

    def test_catalog_and_invocation_branches_match_mcp_tools(self):
        contract = _response_contract(self.operations["get"], "200")
        catalog = contract["example"]
        Draft202012Validator(contract["schema"]).validate(catalog)
        tools = types.ListToolsResult.model_validate(catalog["result"]).tools
        observed = {tool.name: tool for tool in tools}
        expected = {
            name: public_tool(types.Tool.model_validate(native))
            for name, native in descriptors().items()
        }
        self.assertTrue(expected)
        self.assertEqual(len(tools), len(observed))
        self.assertEqual(observed, expected)

        branches = {
            branch["properties"]["name"]["const"]: branch["properties"]
            for branch in self.request_schema["oneOf"]
        }
        self.assertEqual(len(branches), len(self.request_schema["oneOf"]))
        self.assertEqual(branches.keys(), observed.keys())
        for name, branch in branches.items():
            with self.subTest(tool=name):
                arguments = deepcopy(expected[name].input_schema)
                del arguments["properties"]["caller_context"]
                arguments["properties"]["project_root"]["pattern"] = r"\S"
                self.assertEqual(branch["arguments"], arguments)

    def test_invocation_envelope_matches_mcp_routing(self):
        arguments, caller = take_caller_context(
            {
                "project_root": "/project",
                "sql": "SELECT 42",
                "caller_context": {"session_id": "caller"},
            }
        )
        payload = {
            "name": "query_run",
            "arguments": arguments,
            "session_id": caller.session_id,
            "public_base_url": "http://mcp.example/",
        }
        self.assertTrue(self.request_body["required"])
        self.assertCountEqual(self.request_schema["required"], payload)
        validator = Draft202012Validator(self.request_schema)
        validator.validate(payload)
        validator.validate(
            payload | {"session_id": None, "public_base_url": None}
        )
        self.assertFalse(validator.is_valid(payload | {"session_id": " "}))
        self.assertFalse(
            validator.is_valid(payload | {"instance_id": "a" * 64})
        )

        header = next(
            item
            for item in self.post["parameters"]
            if item["name"] == "X-Anechoic-Project-Instance"
        )
        self.assertEqual(header["in"], "header")
        instance = Draft202012Validator(header["schema"])
        instance.validate("a" * 64)
        self.assertFalse(instance.is_valid("b" * 63))
        self.assertFalse(instance.is_valid("x" * 64))

    def test_replies_match_mcp_decoding(self):
        project = {"prefix": "AN", "instance_id": "a" * 64}
        ok = Draft202012Validator(
            _response_contract(self.post, "200")["schema"]
        )
        result = {"value": {"rows": [[42]]}, "text": None}
        ok.validate({"result": result, "project": project})
        self.assertTrue(valid_tool_response(result))
        self.assertFalse(ok.is_valid({"result": result}))

        tool_result = {"outcome": "failed", "diagnostics": ["query failed"]}
        tool_fault = {
            "error": {
                "code": "query_error",
                "message": "query failed",
                "scope": "tool",
                "tool_result": tool_result,
            },
            "project": project,
        }
        ok.validate(tool_fault)
        with self.assertRaises(ToolProtocolError) as caught:
            _raise_fault(tool_fault)
        self.assertEqual(caught.exception.tool_result, tool_result)

        project_fault = {
            "error": {
                "code": "shared_gateway_failure",
                "message": "Backend unavailable",
                "scope": "project",
            },
            "project": None,
        }
        unavailable = _response_contract(self.post, "503")["schema"]
        Draft202012Validator(unavailable).validate(project_fault)
        with self.assertRaises(SharedGatewayRefusal) as caught:
            _raise_fault(project_fault)
        self.assertEqual(caught.exception.code, "shared_gateway_failure")
