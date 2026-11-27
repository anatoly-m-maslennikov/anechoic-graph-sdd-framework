
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import NonCallableMock


MCP_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = (
    MCP_ROOT.parents[1]
    / "IWE_CONSOLE_C43"
    / "APP_IWE_CONSOLE"
    / "FEATURE_IWE_CONSOLE_FRONTEND"
)

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import WORKBENCH_PATH  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError  # noqa: E402


PROJECT_NAME = "anechoic"
PROJECT_PATH = f"{WORKBENCH_PATH}/{PROJECT_NAME}"
API_PATH = f"/anechoic/{PROJECT_NAME}/api"


class FakeWorkbench:
    def __init__(self):
        self.calls = []
        self.contexts = []

    def _validate_call(self, name, arguments):
        if name == "query_page" and (
            not isinstance(arguments.get("query_id"), str)
            or type(arguments.get("offset")) is not int
            or arguments["offset"] < 0
        ):
            raise ToolProtocolError(
                "query_error", "offset must be a non-negative integer"
            )
        if name == "query_load" and not isinstance(
            arguments.get("reference"), str
        ):
            raise ToolProtocolError(
                "query_error", "reference must be a string"
            )
        if name == "query_saved_list":
            limit = arguments.get("limit", 20)
            if type(limit) is not int or not 1 <= limit <= 1000:
                raise ToolProtocolError(
                    "query_error", "limit must be an integer from 1 to 1000"
                )
        if (
            name in {"query_run", "query_check"}
            or name == "view_save"
            and "workspace_id" not in arguments
        ) and not isinstance(arguments.get("sql"), str):
            raise ToolProtocolError("query_error", "sql must be a string")

    async def call_tool(
        self,
        name,
        arguments,
        *,
        public_base_url=None,
        asserted_project_root=None,
    ):
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.workbench_links import (
            public_saved,
            public_workspace,
            validate_reference,
        )

        self.contexts.append((public_base_url, asserted_project_root))
        request = SimpleNamespace(base_url=public_base_url)
        if name == "query_load" and isinstance(
            arguments.get("reference"), str
        ):
            try:
                validate_reference(
                    arguments["reference"],
                    request,
                    self.selection,
                    asserted_project_root,
                )
            except ValueError as error:
                raise ToolProtocolError("query_error", str(error)) from error
        value = await self.call(name, arguments)
        value = public_saved(
            value, request, self.selection, asserted_project_root
        )
        if name in {"workspace_open", "workspace_get"}:
            value = public_workspace(
                value, request, self.selection, asserted_project_root
            )
        return {"value": value, "text": None}

    async def call(self, name, arguments):  # noqa: C901
        self.calls.append((name, arguments))
        self._validate_call(name, arguments)
        if name == "workspace_open":
            return {"workspace_id": arguments["session_id"], "views": []}
        if name == "workspace_get":
            return {"workspace_id": arguments["workspace_id"], "views": []}
        if name == "view_create":
            return {
                "workspace_id": arguments["workspace_id"],
                "view_id": "view-1",
            }
        if name == "view_save" and "workspace_id" in arguments:
            return {
                "workspace_id": arguments["workspace_id"],
                "view_id": arguments["view_id"],
            }
        if name == "query_page":
            if arguments["query_id"] != "query-1":
                raise ToolProtocolError("query_error", "unknown query_id")
            return {
                "query_id": "query-1",
                "columns": [{"name": "value", "type": "VARCHAR"}],
                "rows": [["page two"]],
                "row_count": 2,
                "column_count": 1,
                "offset": arguments["offset"],
                "page_size": arguments.get("page_size", 100),
                "has_more": False,
            }
        if name == "query_schema":
            return {"atoms": []}
        if name == "workbench_status":
            return {"syncing": False, "last_synced_at": None, "audits_pending": False, "last_audit_ms": None, "audit_error": None}
        if name == "query_saved_list":
            return {"items": []}
        if name == "query_load":
            return {"saved_query_id": arguments["reference"], "kind": "query", "sql": "SELECT 1"}
        if name == "view_save":
            value = {"saved_query_id": "w_1", "kind": "view", "sql": arguments["sql"]}
            if arguments.get("name", "").strip():
                value["name"] = arguments["name"]
            return value
        return self._call_sql(name, arguments)

    def _call_sql(self, name, arguments):
        if arguments["sql"] == "bad":
            raise ToolProtocolError("query_error", "bad query")
        if arguments["sql"] == "crash":
            raise RuntimeError("private unexpected connector detail")
        if arguments["sql"] == "large":
            return {
                "query_id": "query-1",
                "columns": [
                    {"name": "item", "type": "VARCHAR"},
                    {"name": "item", "type": "VARCHAR"},
                ],
                "rows": [
                    [f"λ-{index}", f"value-{index}"] for index in range(100)
                ],
                "row_count": 1024,
                "column_count": 2,
                "offset": 0,
                "page_size": arguments.get("page_size", 100),
                "has_more": True,
            }
        if arguments["sql"] == "partial":
            return {
                "query_id": "query-1",
                "rows": [["saved result"]],
                "outcome": "partial",
                "save_error": "journal unavailable",
            }
        if name == "query_check":
            return {"valid": True, "row_count": 1, "column_count": 1}
        value = {
            "query_id": "query-1",
            "columns": [{"name": "value", "type": "VARCHAR"}],
            "rows": [["<script>x</script>"]],
            "row_count": 1,
            "column_count": 1,
            "offset": 0,
            "page_size": arguments.get("page_size", 100),
            "has_more": False,
        }
        if arguments.get("save"):
            value.update({"saved_query_id": "q_1", "kind": "query", "sql": arguments["sql"]})
            if arguments.get("name", "").strip():
                value["name"] = arguments["name"]
        return value


class FakeGateway:
    def __init__(self):
        self.workbench = FakeWorkbench()
        self.roots = []
        self.root = Path.cwd()
        self.tool_blacklist = frozenset()
        self.selection = NonCallableMock(
            spec_set=["project_name", "root", "host_root", "instance_id"],
            project_name=PROJECT_NAME,
            root=self.root,
            host_root=None,
            instance_id="a" * 64,
        )
        self.workbench.selection = self.selection

    async def select_project(self, root):
        if root != "/project":
            raise ValueError("invalid_project_root")
        return {
            "project_name": self.selection.project_name,
            "instance_id": "a" * 64,
        }

    async def call_tool(
        self,
        name,
        arguments,
        *,
        public_base_url=None,
        asserted_project_root=None,
        project_instance_id=None,
    ):
        if name == "unknown" or name in self.tool_blacklist:
            raise ToolProtocolError("tool_unavailable", "Unknown Tool", {
                "outcome": "rejected", "diagnostics": ["Unknown Tool"],
            })
        if "project_root" in arguments:
            asserted_project_root = arguments["project_root"]
            self.roots.append(asserted_project_root)
            arguments = {
                key: value
                for key, value in arguments.items()
                if key != "project_root"
            }
        return await self.workbench.call_tool(
            name,
            arguments,
            public_base_url=public_base_url,
            asserted_project_root=asserted_project_root,
        )
