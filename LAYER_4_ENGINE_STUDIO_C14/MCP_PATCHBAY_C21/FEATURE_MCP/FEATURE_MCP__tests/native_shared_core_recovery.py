"""Check background recovery of one loaded Project in a shared candidate."""

import asyncio
import shlex
import subprocess

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .workbench_docker_support import assert_container_running, image_timeout


KILL_CHILD = """
import os
from pathlib import Path
import signal
import sys

module = os.fsencode(sys.argv[1])
required = set(map(os.fsencode, sys.argv[2:]))
matches = []
for path in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        arguments = path.read_bytes().split(b'\\0')
    except (FileNotFoundError, ProcessLookupError):
        continue
    if (b'-m', module) in zip(arguments, arguments[1:]) and required.issubset(arguments):
        matches.append(int(path.parent.name))
assert len(matches) == 1, (sys.argv[1], matches)
os.kill(matches[0], signal.SIGKILL)
"""

_KERNEL = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"
_ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"


def _pairs(case):
    processes, _ = case._processes()
    pairs = {}
    for pid, _, command in processes:
        if not any(module in command for module in (_KERNEL, _ORCHESTRATOR)):
            continue
        args = shlex.split(command)
        if "-m" not in args or "--instance-id" not in args:
            continue
        module = args[args.index("-m") + 1]
        if module in (_KERNEL, _ORCHESTRATOR):
            instance = args[args.index("--instance-id") + 1]
            pairs.setdefault(instance, {})[module] = pid
    return pairs


async def _wait_for_pair(case, instance, old):
    async with asyncio.timeout(image_timeout(30)):
        while True:
            current = (await asyncio.to_thread(_pairs, case)).get(instance, {})
            if current.keys() == old.keys() and not set(current.values()) & set(old.values()):
                return current
            await asyncio.sleep(0.15)


async def _query_after_recovery(case, session, project):
    args = {"project_root": str(project), "sql": "SELECT 42",
            "result_delivery": "inline", "result_format": "json_matrix"}
    async with asyncio.timeout(image_timeout(45)):
        while True:
            result = await session.call_tool("query_run", args)
            if not result.is_error:
                case.assertEqual([[42]], result.structured_content["rows"])
                return
            # A replacement PID can exist before its initial admission succeeds.
            case.assertIn("project_gateway_busy", str(result.structured_content))
            if image_timeout(45) is None:
                await asyncio.to_thread(assert_container_running, case._shared_candidate_container)
            await asyncio.sleep(0.15)


async def assert_core_recovery(case, endpoint, projects, http, unaffected_query_id):
    base = await asyncio.to_thread(_pairs, case)
    case.assertEqual(2, len(base))
    facades = case._assert_project_processes(projects)
    facades.pop("peer_processes")
    instance, other = sorted(base)
    project = None
    processes, _ = await asyncio.to_thread(case._processes)
    for name in ("alpha", "beta"):
        if any(pid == base[instance][_KERNEL] and str(projects / name) in shlex.split(command)
               for pid, _, command in processes):
            project = name
    case.assertIsNotNone(project)
    sibling = "alpha" if project == "beta" else "beta"
    for module in (_KERNEL, _ORCHESTRATOR):
        await asyncio.to_thread(
            subprocess.run, ["docker", "exec", case._shared_candidate_container, "python", "-B",
                             "-c", KILL_CHILD, module, instance],
            timeout=image_timeout(10), check=True, capture_output=True, text=True,
        )
        base[instance] = await _wait_for_pair(case, instance, base[instance])
        case.assertEqual(base[other], (await asyncio.to_thread(_pairs, case))[other])
        async with streamable_http_client(endpoint, http_client=http) as streams, ClientSession(*streams) as session:
            await session.initialize()
            await _query_after_recovery(case, session, projects / project)
            page = await session.call_tool("query_page", {
                "project_root": str(projects / sibling), "query_id": unaffected_query_id[sibling],
                "caller_context": {"session_id": "candidate-" + sibling},
                "offset": 0, "page_size": 1, "result_delivery": "inline",
            })
            case.assertFalse(page.is_error, page.structured_content)
            case.assertEqual([[f"{sibling.upper()}-S-001"]], page.structured_content["rows"])
        current = case._assert_project_processes(projects)
        current.pop("peer_processes")
        case.assertEqual(facades, current)
