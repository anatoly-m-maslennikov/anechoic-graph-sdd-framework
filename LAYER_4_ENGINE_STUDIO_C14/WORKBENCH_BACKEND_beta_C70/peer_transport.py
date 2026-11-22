"""Use the private HTTP contracts of the selected Project peers."""

import httpx2


async def upstream(socket_path, method, path, *, timeout=10, **kwargs):
    async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=socket_path),
                                 base_url="http://private", timeout=timeout, trust_env=False) as client:
        response = await client.request(method, path, **kwargs)
        data = response.json()
        if not isinstance(data, dict) or set(data) not in ({"result"}, {"error"}):
            raise ValueError("Invalid upstream response")
        return data


def tool_failure(code, message):
    rejected = code in {"tool_input_invalid", "tool_unavailable"}
    diagnostic = "Unknown Tool" if code == "tool_unavailable" else code if rejected else f"{code}: {message}"
    return {"error": {"code": code, "message": message, "tool_result": {
        "outcome": "rejected" if rejected else "failed", "diagnostics": [diagnostic]}}}
