
"""Functional registry generation and generic MCP Provider dispatch."""

from __future__ import annotations

from .native_query_test_support import local_gateway

import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from uuid import uuid4



MCP = Path(__file__).resolve().parents[1]
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.tool_registry_assets import FEATURE_RELATIVE  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import (  # noqa: E402
    load_active_registry,
)



def _provider_source() -> str:
    return '''from mcp import types
class Provider:
    async def call(self, name, arguments):
        return {"name": name, "arguments": arguments}
    async def close(self):
        return None
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema),
            types.Tool(name="blocked", description="Blocked", input_schema=schema))
'''


def _mixed_descriptor_provider_source() -> str:
    return '''from mcp import types
class Provider:
    async def call(self, name, arguments):
        return {"name": name, "arguments": arguments}
    async def close(self):
        return None
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    valid = {"type": "object", "properties": {}, "additionalProperties": False}
    invalid = {"type": "not-a-json-schema-type"}
    return (types.Tool(name="demo", description="Demo", input_schema=valid),
            types.Tool(name="broken", description="Broken", input_schema=invalid))
'''


def _drifting_provider_source() -> str:
    return '''import asyncio
from pathlib import Path
from mcp import types
calls = 0
class Provider:
    async def prepare_arguments(self, name, arguments, context):
        await asyncio.sleep(0)
        registry = Path(__file__).with_name("tool_registry.json")
        registry.write_text(registry.read_text(encoding="utf-8") + "\\n", encoding="utf-8")
        return arguments
    async def call(self, name, arguments):
        global calls
        calls += 1
        return {"ok": True}
    async def close(self):
        return None
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema),)
'''


def _context_provider_source() -> str:
    return '''from mcp import types
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import current_request_context
calls = 0
class Provider:
    async def call(self, name, arguments):
        global calls
        calls += 1
        current = current_request_context()
        return {"native": arguments, "caller": current.session_id if current else None}
    async def close(self):
        return None
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {"session_id": {"type": "string"}}, "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema),)
'''


def _schema_provider_source() -> str:
    return '''from mcp import types
calls = 0
closed = 0
class Provider:
    async def call(self, name, arguments):
        global calls
        calls += 1
        return {"ok": "invalid"}
    async def close(self):
        global closed
        closed += 1
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    input_schema = {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=input_schema, output_schema=output_schema),)
'''


def _lifecycle_provider_source() -> str:
    return '''from mcp import types
created = 0
closed = 0
class Provider:
    async def call(self, name, arguments):
        return {"ok": True}
    async def close(self):
        global closed
        closed += 1
def create_provider(root, gateway):
    global created
    created += 1
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    output = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema, output_schema=output),)
'''


def _saved_id_provider_source() -> str:
    return '''from mcp import types
class Provider:
    async def call(self, name, arguments):
        return {"saved_query_id": "q_0123456789abcdef0123456789abcdef"}
    async def close(self):
        return None
def create_provider(root, gateway):
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    output = {"type": "object", "properties": {"saved_query_id": {"type": "string"}}, "required": ["saved_query_id"], "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema, output_schema=output),)
'''


def _partial_provider_source() -> str:
    return '''from mcp import types
created = 0
closed = 0
class Provider:
    async def close(self):
        global closed
        closed += 1
def create_provider(root, gateway):
    global created
    created += 1
    return Provider()
def tool_descriptors():
    schema = {"type": "object", "properties": {}, "additionalProperties": False}
    return (types.Tool(name="demo", description="Demo", input_schema=schema),)
'''


def _native_gateway(root, parameters=None):
    owner = SimpleNamespace(selection=SimpleNamespace(root=root, parameters=parameters or {}),
                            start=lambda: None, close=lambda: None)
    return local_gateway(root, native_query=owner)



class ToolRegistryFixture:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.package = Path(self.temporary.name) / "package"
        self.feature = self.package / FEATURE_RELATIVE
        self.feature.mkdir(parents=True)
        # Synthetic providers live outside the real Engine package.
        sys.path.insert(0, str(self.feature))
        self.addCleanup(sys.path.remove, str(self.feature))
        self.module = "provider_" + uuid4().hex
        (self.feature / f"{self.module}.py").write_text(_provider_source(), encoding="utf-8")
        self._write_inventory()


    def tearDown(self) -> None:
        sys.modules.pop(self.module, None)


    def _write_inventory(self, *, blacklist: list[str] | None = None) -> None:
        payload = {
            "schema_version": 1,
            "mcp_blacklist": ["blocked"] if blacklist is None else blacklist,
            "providers": [{
                "provider_id": "demo_provider",
                "module": self.module,
                "factory": "create_provider",
                "descriptor_factory": "tool_descriptors",
            }],
        }
        (self.feature / "tool_providers.json").write_text(json.dumps(payload), encoding="utf-8")


    def _write_provider(self, source: str) -> None:
        sys.modules.pop(self.module, None)
        (self.feature / f"{self.module}.py").write_text(source, encoding="utf-8")


    def _registry(self, root: Path, gateway: object):
        return load_active_registry(self.feature, root, gateway)


