"""Use the shared peer owner's private selection and lease protocol."""

import asyncio
from contextlib import asynccontextmanager, suppress
import json
from typing import Any

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Binding(StrictModel):
    root: str
    control_root: str
    control_relative: str
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: str
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, Any]
    host_root: str | None
    tool_blacklist: list[str]
    release_workflows_enabled: bool


class WorkerBinding(StrictModel):
    root: str
    control_root: str
    manifest_path: str
    manifest_sha256: str
    project_prefix: str


class Lease(StrictModel):
    database_socket: str
    orchestrator_socket: str
    worker_binding: WorkerBinding


class Process(StrictModel):
    instance_id: str
    kernel_pid: int
    orchestrator_pid: int


class Status(StrictModel):
    loaded_project_count: int
    max_loaded_projects: int
    loaded_project_processes: list[Process]


async def exchange(reader, writer, message):
    writer.write(message)
    await writer.drain()
    line = await reader.readline()
    if not line.endswith(b"\n"):
        raise RuntimeError("Incomplete peer owner response")
    response = json.loads(line)
    if isinstance(response, dict) and set(response) == {"result"}:
        return response["result"]
    if (
        isinstance(response, dict)
        and set(response) == {"error", "message"}
        and isinstance(response["message"], str)
    ):
        if response["error"] == "ValueError":
            raise ValueError(response["message"])
        if response["error"] == "RuntimeError":
            raise RuntimeError(response["message"])
    raise RuntimeError("Invalid peer owner response")


def encode(request):
    return json.dumps(request).encode("utf-8") + b"\n"


class Owner:
    def __init__(self, path):
        self.path = path

    @asynccontextmanager
    async def connection(self):
        reader, writer = await asyncio.open_unix_connection(
            self.path, limit=1024 * 1024
        )
        try:
            yield reader, writer
        finally:
            writer.close()
            with suppress(OSError):
                await writer.wait_closed()

    async def request(self, request):
        async with asyncio.timeout(45), self.connection() as (reader, writer):
            return await exchange(reader, writer, encode(request))

    async def select(self, root):
        request = {"operation": "select", "project_root": root}
        return Binding.model_validate(await self.request(request))

    async def status(self):
        return Status.model_validate(
            await self.request({"operation": "status"})
        )

    @asynccontextmanager
    async def lease(self, binding, *, start=True):
        async with self.connection() as (reader, writer):
            request = {
                "operation": "lease",
                "binding": binding.model_dump(),
                "start": start,
            }
            result = await exchange(reader, writer, encode(request))
            try:
                yield None if result is None else Lease.model_validate(result)
            finally:
                with suppress(OSError, RuntimeError, ValueError, TimeoutError):
                    async with asyncio.timeout(2):
                        await exchange(reader, writer, b"R")
