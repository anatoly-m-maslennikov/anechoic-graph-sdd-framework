"""Exercise persisted ingestion warnings through the real shared API."""

import asyncio
import os
import sys
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path

import httpx2

from .test_archive_process import ENGINE, write_manifest
from .test_startup_checkpoint_process import write_ticket

ISSUES = "SELECT source, relative_path, code FROM ops_ingestion_issues ORDER BY relative_path"
ATOMS = 'SELECT reference, "content.summary" FROM mrt_atoms WHERE reference LIKE \'AN-T-%\' ORDER BY reference'


class IngestionProcessTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temporary = self.enterContext(tempfile.TemporaryDirectory(prefix="ane-ingestion-", dir="/tmp"))
        self.runtime = Path(temporary).resolve()
        self.root = self.runtime / "project"
        self.root.mkdir()
        manifest = write_manifest(self.root)
        self.tickets = manifest.parent / "__TKT" / "TASKS"
        self.tickets.mkdir(parents=True)
        self.settings = self.runtime / "host.toml"
        self.settings.write_text(f'schema_version=1\n[shared_mcp]\nproject_root="{self.root}"\n'
                                 'http_port=8092\nmax_loaded_projects=1\n')
        self.env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_PROFILE": "test",
                    "ANECHOIC_WORKBENCH_STORAGE": "disk", "ANECHOIC_JOURNAL_STORAGE": "files",
                    "ANECHOIC_ARCHIVES": "load", "ANECHOIC_LOG_LEVEL": "ERROR",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))}

    async def start(self, module, *arguments):
        process = await asyncio.create_subprocess_exec(sys.executable, "-B", "-P", "-m", module, *arguments,
                                                       cwd=ENGINE, env=self.env, stdin=asyncio.subprocess.PIPE)
        return process

    async def stop(self, process):
        process.stdin.close()
        try:
            await asyncio.wait_for(process.wait(), 20)
        except TimeoutError:
            process.kill()
            await process.wait()
            self.fail("Shared process did not stop on EOF")
        self.assertEqual(0, process.returncode)

    async def wait_socket(self, path, process):
        async with asyncio.timeout(30):
            while not path.is_socket():
                self.assertIsNone(process.returncode, f"Process exited before creating {path}")
                await asyncio.sleep(0.02)

    @asynccontextmanager
    async def session(self):
        owner_socket, api_socket = self.runtime / "owner.sock", self.runtime / "api.sock"
        owner = await self.start("ORCHESTRATOR_beta_C68.shared_peer_owner", "--socket", str(owner_socket),
                                 "--host-settings", str(self.settings))
        api = None
        try:
            await self.wait_socket(owner_socket, owner)
            api = await self.start("API_MIXER_beta_C82.shared_runtime", "--socket", str(api_socket),
                                   "--peer-owner-socket", str(owner_socket))
            await self.wait_socket(api_socket, api)
            async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=str(api_socket)),
                                          base_url="http://private", timeout=90, trust_env=False) as client:
                yield client, owner.pid
        finally:
            try:
                if api is not None:
                    await self.stop(api)
            finally:
                await self.stop(owner)

    async def invoke(self, client, name, arguments):
        request = {"name": name, "arguments": {"project_root": str(self.root), **arguments},
                   "session_id": None, "public_base_url": None}
        return (await client.post("/tools", json=request)).json()

    async def rows(self, client, sql):
        result = await self.invoke(client, "query_run", {"sql": sql, "result_delivery": "inline"})
        self.assertIn("result", result, result)
        return result["result"]["value"]["rows"]

    async def wait_rows(self, client, sql, expected):
        async with asyncio.timeout(60):
            while await self.rows(client, sql) != expected:
                await asyncio.sleep(0.05)

    def database_identity(self):
        database, = (self.root / ".anechoic_runtime/workbench/beta").glob("*.duckdb")
        info = database.stat()
        return database, info.st_dev, info.st_ino

    async def test_warning_survives_restart_and_clears_after_repair(self):
        ticket = self.tickets / "AN-T-1-TASK--Broken.md"
        ticket.write_text("---\nidentity: [invalid\n")
        issue = [["atom", ticket.relative_to(self.root).as_posix(), "parse_error"]]
        async with self.session() as (client, first_pid):
            first = await self.invoke(client, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
            self.assertIn("result", first, first)
            self.assertEqual(issue, await self.rows(client, ISSUES))
        database = self.database_identity()
        async with self.session() as (client, next_pid):
            self.assertNotEqual(first_pid, next_pid)
            restarted = await self.invoke(client, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
            self.assertEqual(first["project"], restarted["project"])
            self.assertEqual(issue, await self.rows(client, ISSUES))
        self.assertEqual(database, self.database_identity())
        write_ticket(self.tickets, 1, "Broken")
        ticket.write_text(ticket.read_text().replace("\nBroken\n", "\nRepaired Ticket\n"))
        async with self.session() as (client, _):
            self.assertEqual([["AN-T-1", "Repaired Ticket"]], await self.rows(client, ATOMS))
            self.assertEqual([], await self.rows(client, ISSUES))
        self.assertEqual(database, self.database_identity())

    async def test_archive_duplicate_excluded_and_reconciled(self):
        live = write_ticket(self.tickets, 1, "Current")
        archived = write_ticket(self.tickets / "09_archived", 1, "Duplicate", archived=True)
        write_ticket(self.tickets, 2, "Usable")
        issues = [[source, path.relative_to(self.root).as_posix(), "duplicate_revision"]
                  for source, path in (("archive", archived), ("atom", live))]
        async with self.session() as (client, _):
            await self.wait_rows(client, ISSUES, issues)
            self.assertEqual([["AN-T-2", "Usable"]], await self.rows(client, ATOMS))
            archived.unlink()
            await self.wait_rows(client, ATOMS, [["AN-T-1", "Current"], ["AN-T-2", "Usable"]])
            self.assertEqual([], await self.rows(client, ISSUES))
