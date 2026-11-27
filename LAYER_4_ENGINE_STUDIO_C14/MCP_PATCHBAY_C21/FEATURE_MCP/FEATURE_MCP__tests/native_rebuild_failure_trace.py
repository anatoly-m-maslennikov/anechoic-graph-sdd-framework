(
    'Trace a real saved-result rebuild failure through the Workbench HTTP '
    'route.'
)

import asyncio
from contextlib import redirect_stderr
from inspect import getsourcefile
from io import StringIO
import json
from unittest.mock import patch

import httpx2

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    create_http_app as create_app,
)
from .native_query_test_support import create_native_gateway
from .test_native_query_stdio import (
    CONTROL,
    NativeQueryStdioTests,
    _native_inputs,
)


class DiagnosticSink(StringIO):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def write(self, text):
        result = super().write(text)
        if (
            "Workbench rebuild failed" in self.getvalue()
            and "diagnostic" not in self.events
        ):
            self.events.append("diagnostic")
        return result


def response_body(response, events):
    try:
        body = response.json()
    except ValueError as error:
        raise ValueError(
            f"Invalid HTTP observation: {response.status_code} non-JSON body"
        ) from error
    if 200 <= response.status_code < 300:
        events.append("clientSuccess")
    elif (
        400 <= response.status_code < 600
        and isinstance(body, dict)
        and isinstance(body.get("error"), str)
        and body["error"].strip()
    ):
        events.append("clientError")
    else:
        raise ValueError(
            f"Invalid HTTP observation: {response.status_code} {body!r}"
        )
    return body


def prepare_failure(store):
    store._connection.execute("CREATE TABLE input (value INTEGER)")
    store._connection.execute("INSERT INTO input VALUES (1)")
    store.run("SELECT value FROM input")
    store._connection.execute(
        "ALTER TABLE input RENAME COLUMN value TO renamed"
    )


async def trace():
    fixture = NativeQueryStdioTests()
    fixture.setUp()
    events = []
    stderr = DiagnosticSink(events)
    try:
        app = create_app(fixture.root, gateway_factory=lambda root, control: create_native_gateway(
            root, control, _native_inputs()), control_root=CONTROL)
        async with app.starlette_app.router.lifespan_context(app.starlette_app):
            owner = app.gateway._native_query
            store = owner._owner()
            prepare_failure(store)
            prepare = store.prepare_result_rebuild
            commit = store.commit_result_rebuild
            replace = owner._workspaces.replace_result_ids

            def observe_prepare(*args, **kwargs):
                try:
                    return prepare(*args, **kwargs)
                except Exception:
                    events.append("failed")
                    raise

            def observe_commit(*args, **kwargs):
                result = commit(*args, **kwargs)
                events.append("published")
                return result

            def observe_replace(*args, **kwargs):
                result = replace(*args, **kwargs)
                events.append("published")
                return result

            with (redirect_stderr(stderr), patch.object(store, "prepare_result_rebuild", observe_prepare),
                  patch.object(store, "commit_result_rebuild", observe_commit),
                  patch.object(owner._workspaces, "replace_result_ids", observe_replace)):
                async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                              base_url="http://127.0.0.1:18093") as client:
                    response = await client.post("/anechoic/Anechoic/api/rebuild",
                                                 json={"target": "workbench_results"})
            body = response_body(response, events)
            return {"events": events, "http_status": response.status_code, "body": body,
                    "stderr": stderr.getvalue(), "source": getsourcefile(owner.rebuild)}
    finally:
        fixture.doCleanups()


if __name__ == "__main__":
    print(json.dumps(asyncio.run(trace())))
