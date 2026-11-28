"""Exercise the private peer-owner CLI with real Project peer processes."""

import asyncio
from contextlib import suppress
import os
from pathlib import Path
import signal
import unittest

import httpx2

from ._shared_peer_fixture import _response, PeerOwnerFixture


class PeerOwnerTests(PeerOwnerFixture, unittest.IsolatedAsyncioTestCase):
    async def test_select_applies_mounted_storage_settings(self):
        settings = self.projects / ".anechoic_runtime_config.toml"
        settings.write_text(
            'schema_version=1\n[container]\nhttp_port=7777\nmode="projects"\n'
            'workbench_storage="memory"\njournal_storage="duckdb"\n'
        )
        await self._start_owner(settings=settings)
        for project in (self.first, self.second):
            with self.subTest(project=project["root"]):
                selected = await self._select(project_root=project["root"])
                self.assertEqual(selected["result"]["root"], project["root"])
                self.assertEqual(
                    selected["result"]["parameters"]["runtime"],
                    {
                        "iwe_console": {"storage": "memory"},
                        "journal": {"storage": "duckdb"},
                    },
                )

    async def test_select_returns_lease_binding_without_starting_peers(self):
        await self._start_owner()
        self.assertEqual(
            {"error": "ValueError", "message": "missing_project_root"},
            await self._select(),
        )
        for value in (None, "", "alpha", 1):
            self.assertEqual(
                {"error": "ValueError", "message": "invalid_project_root"},
                await self._select(project_root=value),
            )
        self.assertEqual(
            {"error": "ValueError", "message": "outside_project_root"},
            await self._select(project_root=str(self.projects.parent)),
        )
        selected = (await self._select(project_root=self.first["root"]))[
            "result"
        ]
        self.assertEqual(set(self.first), set(selected))
        self.assertEqual(self.first["root"], selected["root"])
        self.assertEqual(self.first["instance_id"], selected["instance_id"])
        self.assertEqual(
            {
                "iwe_console": {"storage": "disk"},
                "journal": {"storage": "files"},
            },
            selected["parameters"]["runtime"],
        )
        async with self._lease(selected, start=False) as (reader, _):
            self.assertEqual({"result": None}, await _response(reader))
        self.assertEqual(0, (await self._status())["loaded_project_count"])

    async def test_lease_validates_request_and_binding_without_coercion(self):
        await self._start_owner()
        invalid_request = (
            {"operation": "lease", "binding": self.first, "start": 1},
            {
                "operation": "lease",
                "binding": self.first,
                "start": True,
                "extra": 1,
            },
            {"operation": "lease", "binding": self.first},
        )
        for request in invalid_request:
            async with self._connection(request) as (reader, _):
                self.assertEqual(
                    {
                        "error": "ValueError",
                        "message": "Invalid peer owner request",
                    },
                    await _response(reader),
                )
        for binding in (
            self.first | {"tool_blacklist": [1]},
            self.first | {"release_workflows_enabled": 1},
            self.first | {"extra": "unexpected"},
            None,
        ):
            async with self._lease(binding, start=False) as (reader, _):
                self.assertEqual(
                    {
                        "error": "RuntimeError",
                        "message": "Invalid Project admission response",
                    },
                    await _response(reader),
                )
        async with self._lease(self.first, start=False) as (reader, _):
            self.assertEqual({"result": None}, await _response(reader))

    async def test_changed_host_settings_rejects_selection(self):
        await self._start_owner()
        settings = self.socket.with_name("host.toml")
        settings.write_text(
            settings.read_text() + "\n[logging]\nlevel='WARNING'\n"
        )
        self.assertEqual(
            {"error": "ValueError", "message": "host_configuration_stale"},
            await self._select(project_root=self.first["root"]),
        )

    async def test_select_requires_explicit_project_on_single_project_host(
        self,
    ):
        await self._start_owner(project_root=self.first["root"])
        self.assertEqual(
            {"error": "ValueError", "message": "missing_project_root"},
            await self._select(),
        )
        self.assertEqual(
            {"error": "ValueError", "message": "outside_project_root"},
            await self._select(project_root=self.second["root"]),
        )
        selected = (await self._select(project_root=self.first["root"]))[
            "result"
        ]
        self.assertEqual(self.first["instance_id"], selected["instance_id"])

    async def test_disconnect_releases_held_project(self):
        await self._start_owner()
        async with self._lease(self.first) as (reader, _):
            held = await _response(reader)
            self.assertIn("result", held, held)
            self.assertTrue(
                Path(held["result"]["database_socket"]).is_socket()
            )
            await self._assert_busy(self.second)
        peers = await self._acquire(self.second)
        self.assertTrue(Path(peers["orchestrator_socket"]).is_socket())
        self.assertFalse(Path(held["result"]["database_socket"]).exists())
        report = await self._status()
        self.assertEqual(1, report["loaded_project_count"])
        self.assertEqual(
            self.second["instance_id"],
            report["loaded_project_processes"][0]["instance_id"],
        )
        async with self._lease(self.first, start=False) as (reader, _):
            self.assertEqual({"result": None}, await _response(reader))
        self.assertTrue(
            Path(
                (await self._acquire(self.first))["database_socket"]
            ).is_socket()
        )

    async def test_disconnect_during_start_returns_slot(self):
        await self._start_owner()
        storage = (
            Path(self.first["root"])
            / ".anechoic_runtime"
            / "iwe_console"
            / "beta"
        )
        async with self._lease(self.first) as (reader, _):
            reply = asyncio.create_task(_response(reader))
            try:
                async with asyncio.timeout(5):
                    while not storage.is_dir():
                        self.assertFalse(reply.done())
                        await asyncio.sleep(0.01)
                await self._assert_busy(self.second)
                self.assertFalse(
                    reply.done(), "The cold lease already completed"
                )
            finally:
                reply.cancel()
                with suppress(asyncio.CancelledError):
                    await reply
        peers = await self._acquire(self.second)
        self.assertEqual(self.second["root"], peers["worker_binding"]["root"])

    async def test_owner_rejects_binding_with_a_foreign_manifest(self):
        await self._start_owner()
        wrong = self.first | {"manifest_path": self.second["manifest_path"]}
        async with self._lease(wrong) as (reader, _):
            self.assertEqual(
                {
                    "error": "ValueError",
                    "message": "project_declarations_stale",
                },
                await _response(reader),
            )
        self.assertEqual(0, (await self._status())["loaded_project_count"])

    async def test_recovery_waits_for_active_lease_to_drain(self):
        await self._start_owner()
        async with self._lease(self.first) as (reader, _):
            self.assertIn("result", await _response(reader))
            instance = self.first["instance_id"]
            old = (await self._peer_pids())[instance]
            os.kill(old[0], signal.SIGKILL)
            await asyncio.sleep(0.4)
            self.assertEqual(old, (await self._peer_pids())[instance])
            await self._assert_busy(self.first)
        self.assertIn(instance, await self._wait_for_pair(instance, old))

    async def test_recovers_idle_project_after_either_peer_dies(self):
        await self._start_owner(maximum=2)
        await self._acquire(self.first)
        await self._acquire(self.second)
        first, second = self.first["instance_id"], self.second["instance_id"]
        current = await self._peer_pids()
        other = current[second]
        for index in (0, 1):
            with self.subTest(killed=("kernel", "orchestrator")[index]):
                old = current[first]
                os.kill(old[index], signal.SIGKILL)
                await self._wait_for_exit(old[1 - index])
                current = await self._wait_for_pair(first, old)
                self.assertEqual({first, second}, set(current))
                self.assertEqual(other, current[second])
        async with self._lease(self.first, start=False) as (reader, _):
            result = (await _response(reader))["result"]
            transport = httpx2.AsyncHTTPTransport(
                uds=result["database_socket"]
            )
            async with httpx2.AsyncClient(
                transport=transport, base_url="http://private", trust_env=False
            ) as kernel:
                health = (await kernel.get("/health")).json()["result"]
            self.assertIs(True, health["ready"])
            self.assertEqual(
                self.first["manifest_sha256"], health["manifest_sha256"]
            )
            self.assertIsNotNone(health["generation"])
