"""Exercise the shared Backend contract without opening a second process."""

from contextlib import asynccontextmanager

import httpx2

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.shared_backend_process import (
    create_app,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import SharedBackendGateway


@asynccontextmanager
async def backend_gateway(config, session_factory):
    app = create_app(config, gateway_factory=session_factory)
    gateway = SharedBackendGateway(config)
    async with app.router.lifespan_context(app):
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://anechoic-backend",
        ) as client:
            gateway._http = client
            await gateway._load_catalog()
            yield gateway
