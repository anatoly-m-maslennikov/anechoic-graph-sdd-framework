"""Check that the opt-in HTTP MCP service is ready and accepts a session."""
import asyncio
import os
import signal


async def check():
    import httpx2
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async with httpx2.AsyncClient(trust_env=False, follow_redirects=False, timeout=3) as client:
        response = await client.get("http://127.0.0.1:8092/anechoic/health")
        status = response.json() if response.status_code == 200 else {}
        if not isinstance(status, dict) or status.get("state") != "ready":
            raise RuntimeError("MCP service is not ready")
        async with streamable_http_client(
            "http://127.0.0.1:8092/anechoic/mcp", http_client=client
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                await session.send_ping()


if __name__ == "__main__" and os.getenv("ANECHOIC_MCP_HTTP_HEALTHCHECK") == "1":
    signal.alarm(4)
    asyncio.run(check())
