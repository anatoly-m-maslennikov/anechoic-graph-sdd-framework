"""Exchange HTTP cases with the isolated provider subprocess."""

from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[7]
BRIDGE = ROOT / (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
    "FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/"
    "generated_http_server.py"
)


@pytest.fixture(scope="module")
def bridge():
    process = subprocess.Popen(
        [sys.executable, "-B", str(BRIDGE)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
    yield process
    process.stdin.close()
    process.wait(timeout=10)
    assert process.returncode == 0


def bridge_response(line):
    result = json.loads(line)
    response = httpx.Response(
        result["status"],
        content=result["body"],
        headers=result["headers"],
        request=httpx.Request("POST", "http://test/tools"),
    )
    response.elapsed = timedelta()
    return response


def invoke(bridge, body, mode="normal"):
    bridge.stdin.write(json.dumps({"body": body, "mode": mode}) + "\n")
    bridge.stdin.flush()
    return bridge_response(bridge.stdout.readline())


def provider_responses(root, calls):
    messages = "".join(
        json.dumps({"body": body, "mode": mode}) + "\n" for body, mode in calls
    )
    process = subprocess.run(
        [sys.executable, "-B", str(BRIDGE), str(root)],
        input=messages,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    return [bridge_response(line) for line in process.stdout.splitlines()]
