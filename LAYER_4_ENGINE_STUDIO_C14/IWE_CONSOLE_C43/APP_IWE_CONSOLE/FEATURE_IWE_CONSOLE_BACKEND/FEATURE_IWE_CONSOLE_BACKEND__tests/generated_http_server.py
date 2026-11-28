"""Test-only JSON-lines bridge to the production ASGI Tool callback."""

from unittest.mock import NonCallableMock
import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

import duckdb
import httpx2
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.backend_tool_api import (
    BackendToolAPI,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.registry_workbench_provider import (
    create_provider,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.tool_registry_runtime import (
    ActiveToolRegistry,
    ProviderBinding,
    RegisteredTool,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.workbench_operations import (
    WorkbenchOperations,
)
from jsonschema import Draft202012Validator
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    NativeQueryInputs,
    NativeQueryOwner,
    QueryStore,
)
from starlette.applications import Starlette
from starlette.routing import Route
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__tests.query.test_backend_tool_status \
    import make_tool_app  # fmt: skip


@asynccontextmanager
async def pilot_app(state):
    app = make_tool_app()
    api = app.routes[0].endpoint.__self__
    asset = Path(__file__).resolve().parents[1] / "tool_registry.json"
    registry_data = json.loads(asset.read_bytes())
    (schema,) = (
        tool["inputSchema"]
        for provider in registry_data["providers"]
        for tool in provider["tools"]
        if tool["name"] == "query_run"
    )

    class QueryOwner:
        def run(self, sql, **options):
            if state["mode"] == "failure":
                raise RuntimeError("private failure")
            return {"ok": True}

    operations = WorkbenchOperations(query_owner=QueryOwner())

    async def call(name, arguments):
        return operations.call(name, arguments)

    gateway = NonCallableMock(
        spec_set=["selection", "workbench"],
        selection=api._selection,
        workbench=NonCallableMock(spec_set=["call"], call=call),
    )
    binding = ProviderBinding(
        factory=create_provider, root=Path("/test"), gateway=gateway
    )
    tool = RegisteredTool(
        binding=binding,
        input_validator=Draft202012Validator(schema),
        output_validator=None,
    )
    registry = ActiveToolRegistry(
        tools=(),
        routes={"query_run": tool},
        bindings=(binding,),
        global_blacklist=frozenset(),
        asset_root=Path("/test"),
        registry_revision="test",
        inventory_revision="test",
    )
    api._registry = registry
    with patch.object(ActiveToolRegistry, "ensure_current"):
        yield app


def _provider_selection(root):
    return NonCallableMock(
        spec_set=[
            "root",
            "host_root",
            "instance_id",
            "parameters",
            "control_relative",
        ],
        root=root,
        host_root=None,
        instance_id="test",
        parameters={},
        control_relative=Path("_anechoic_test"),
    )


@asynccontextmanager
async def provider_app(root, state):
    selection = _provider_selection(root)
    inputs = NativeQueryInputs(lambda *_: None, frozenset(), {})
    owner = NativeQueryOwner(selection, inputs)
    with duckdb.connect(
        config={"enable_external_access": False}
    ) as connection:
        with patch(
            f"{QueryStore.__module__}._connect", return_value=connection
        ):
            owner._store = QueryStore(native=True)
        owner._capture = object()
        operations = WorkbenchOperations(query_owner=owner)

        def call(name, arguments):
            if state["mode"] == "failure":
                raise RuntimeError("private failure")
            return operations.call(name, arguments)

        def select_project(_):
            if state["mode"] == "stale_binding":
                raise ValueError("Project binding changed")
            return selection

        api = BackendToolAPI(owner, {"workbench": call})
        app = Starlette(routes=[Route("/", api.invoke, methods=["POST"])])
        with patch(
            f"{BackendToolAPI.__module__}.pinned_project",
            side_effect=select_project,
        ):
            try:
                yield app
            finally:
                await api.close()
                operations.close()


async def serve():
    state = {}
    context = (
        provider_app(Path(sys.argv[1]), state)
        if len(sys.argv) > 1
        else pilot_app(state)
    )
    with patch(
        f"{BackendToolAPI.__module__}.report_failure",
        return_value=(None, None),
    ):
        async with (
            context as app,
            httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app), base_url="http://test"
            ) as client,
        ):
            for line in sys.stdin:
                request = json.loads(line)
                state["mode"] = request["mode"]
                response = await client.post("/", json=request["body"])
                print(
                    json.dumps(
                        {
                            "status": response.status_code,
                            "headers": dict(response.headers),
                            "body": response.text,
                        }
                    ),
                    flush=True,
                )


asyncio.run(serve())
