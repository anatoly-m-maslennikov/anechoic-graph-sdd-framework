"""HTTP requests for the Workbench Docker canary."""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request(url: str, *, method: str = "GET", payload: dict | None = None) -> tuple[int, dict | str]:
    body = None if payload is None else json.dumps(payload).encode()
    target = Request(url, data=body, method=method, headers={"content-type": "application/json"})
    try:
        with urlopen(target, timeout=60) as response:  # noqa: S310 -- loopback test server
            data = response.read().decode()
            return response.status, json.loads(data) if response.headers.get_content_type() == "application/json" else data
    except HTTPError as error:
        with error:
            data = error.read().decode()
        return error.code, json.loads(data) if data else {}
