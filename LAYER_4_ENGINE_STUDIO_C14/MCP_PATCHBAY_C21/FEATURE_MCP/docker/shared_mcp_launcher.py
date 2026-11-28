"""Prepare or explicitly start one host-wide HTTP MCP container."""

from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_support.\
    shared_support__shared import MCP_PATH  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_support.\
    shared_support__shared import (  # noqa: E402
    SharedLaunchError,
    health_ready,
    inspect_runtime,
    prepare_config,
)


async def _probe(port, project_root):
    from httpx2 import AsyncClient
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    endpoint = f"http://127.0.0.1:{port}{MCP_PATH}"
    async with AsyncClient(
        trust_env=False, follow_redirects=False, timeout=420
    ) as client:
        async with streamable_http_client(
            endpoint, http_client=client
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                if project_root is not None:
                    result = await session.call_tool(
                        "query_schema",
                        {"project_root": str(project_root)},
                        read_timeout_seconds=400,
                    )
                    if getattr(result, "is_error", True):
                        raise ValueError(
                            "The runtime could not open the selected Project"
                        )


class SharedMcpLauncher:
    """No Docker call is made until ``apply`` is explicitly requested."""

    def __init__(
        self,
        runner: Callable[..., Any] | None = None,
        opener: Callable[..., Any] | None = None,
        sleeper=time.sleep,
        clock=time.monotonic,
    ):
        self.runner = runner or subprocess.run
        self.opener = opener or urlopen
        self.sleeper = sleeper
        self.clock = clock

    def prepare(
        self,
        settings_path=None,
        image=None,
        *,
        compose_file=None,
        timeout=None,
        mounted_folder=None,
        readiness_timeout=None,
    ):
        return prepare_config(
            settings_path,
            image,
            compose_file=compose_file,
            timeout=timeout,
            mounted_folder=mounted_folder,
            readiness_timeout=readiness_timeout,
        )

    def _docker(self, command, environment, timeout):
        try:
            return self.runner(
                command,
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except Exception:
            return None

    def apply(
        self,
        settings_path=None,
        image=None,
        *,
        compose_file=None,
        timeout=None,
        readiness_timeout=None,
        mounted_folder=None,
        verify_mcp=False,
    ):
        prepared = self.prepare(
            settings_path,
            image,
            compose_file=compose_file,
            timeout=timeout,
            mounted_folder=mounted_folder,
            readiness_timeout=readiness_timeout,
        )
        readiness_budget = prepared["readiness_timeout"]
        started = self._docker(
            prepared["command"],
            prepared["environment"],
            prepared["startup_timeout"] + 10,
        )
        if started is None or getattr(started, "returncode", 1) != 0:
            return {
                key: prepared[key]
                for key in (
                    "service",
                    "image",
                    "settings_path",
                    "projects_root",
                    "http_port",
                )
            } | {
                "outcome": "failed",
                "ready": False,
                "condition": "docker_start_failed",
                "docker_returncode": getattr(started, "returncode", None),
            }
        result = self._await_readiness(prepared, readiness_budget)
        if verify_mcp and result["ready"]:
            return self._verify_mcp(prepared, result)
        return result

    @staticmethod
    def _verify_mcp(prepared, result):
        config = prepared["config"]
        project_root = config.projects_root if config.single_project else None
        try:
            asyncio.run(
                asyncio.wait_for(
                    _probe(config.http_port, project_root), timeout=420
                )
            )
        except Exception:
            return result | {
                "outcome": "failed",
                "ready": False,
                "condition": "mcp_verification_failed",
            }
        return result

    def _await_readiness(self, prepared, readiness_budget):
        deadline = self.clock() + readiness_budget
        while self.clock() < deadline:
            observed = inspect_runtime(
                self._docker, prepared, deadline, self.clock
            )
            if observed is False:
                return {
                    "outcome": "failed",
                    "ready": False,
                    "condition": "runtime_mismatch",
                    "service": "shared-mcp",
                }
            if (
                observed
                and health_ready(
                    self.opener, prepared["http_port"], deadline, self.clock
                )
                and self.clock() <= deadline
            ):
                return {
                    "outcome": "started",
                    "ready": True,
                    "condition": "ready",
                    "service": "shared-mcp",
                    "image": prepared["image"],
                    "http_port": prepared["http_port"],
                    "shared_runtime_id": prepared["shared_runtime_id"],
                }
            remaining = deadline - self.clock()
            if remaining <= 0:
                break
            self.sleeper(min(0.25, remaining))
        return {
            "outcome": "started",
            "ready": False,
            "condition": "readiness_failed",
            "service": "shared-mcp",
        }


Launcher = SharedMcpLauncher


def prepare(settings_path=None, image=None, **kwargs):
    return SharedMcpLauncher().prepare(settings_path, image, **kwargs)


def apply(settings_path=None, image=None, **kwargs):
    return SharedMcpLauncher().apply(settings_path, image, **kwargs)


def _public_result(result):
    public = {
        key: value
        for key, value in result.items()
        if key not in {"config", "environment"}
    }
    if result.get("mode") == "dry-run":
        public["environment"] = {
            key: value
            for key, value in result["environment"].items()
            if key.startswith("ANECHOIC_")
        }
    return public


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    locator = parser.add_mutually_exclusive_group()
    locator.add_argument("--host-settings", "--settings", dest="settings_path")
    locator.add_argument("--mounted-folder", type=Path)
    parser.add_argument("--image")
    parser.add_argument("--compose-file", type=Path)
    parser.add_argument("--startup-timeout", type=int, default=None)
    parser.add_argument("--readiness-timeout", type=int, default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify-mcp", action="store_true")
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if args.verify_mcp and not args.apply:
        parser.error("--verify-mcp requires --apply")
    try:
        launcher = SharedMcpLauncher()
        result = (launcher.apply if args.apply else launcher.prepare)(
            args.settings_path,
            args.image,
            compose_file=args.compose_file,
            timeout=args.startup_timeout,
            mounted_folder=args.mounted_folder,
            readiness_timeout=args.readiness_timeout,
            **(
                {
                    "verify_mcp": args.verify_mcp,
                }
                if args.apply
                else {}
            ),
        )
    except SharedLaunchError as error:
        result = {
            "outcome": "refused",
            "ready": False,
            "condition": str(error),
        }
    print(
        json.dumps(
            _public_result(result),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return (
        0
        if result.get("mode") == "dry-run" or result.get("ready") is True
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
