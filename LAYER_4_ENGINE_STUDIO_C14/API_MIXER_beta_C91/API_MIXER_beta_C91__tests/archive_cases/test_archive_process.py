"""Exercise live projection updates while the real Archive Worker is \
delayed."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ._archive_cases_1 import ArchiveCases1
from ._archive_cases_2 import ArchiveCases2
from ._archive_cases_3 import ArchiveCases3
from ._archive_process_fixture import ArchiveProcessFixture
from ._archive_sources import (
    API as API,
    ENGINE as ENGINE,
    INSTANCE as INSTANCE,
    OWNER as OWNER,
    write_manifest as write_manifest,
    write_ticket as write_ticket,
)


class ArchiveProcessTests(
    ArchiveProcessFixture, ArchiveCases1, ArchiveCases2, ArchiveCases3,
    unittest.TestCase,
):
    def setUp(self):
        self.directory = Path(
            self.enterContext(
                tempfile.TemporaryDirectory(prefix="ane-archive-", dir="/tmp")
            )
        ).resolve()
        self.root = self.directory / "project"
        self.root.mkdir()
        manifest = write_manifest(self.root)
        self.control = manifest.parent
        self.tickets = self.control / "__TICKETS" / "TASKS"
        self.seed_tickets()
        self.prepare_process(manifest)

    def call(self, client, name, arguments):
        return client.post(
            "/tools",
            json={
                "name": name,
                "arguments": arguments,
                "instance_id": INSTANCE,
                "session_id": "archive-test",
                "public_base_url": None,
                "asserted_project_root": None,
            },
        ).json()

    def rows(self, client):
        query = {
            "sql": (
                'SELECT reference, status_group, "content.summary" '
                "FROM main.atoms "
                "WHERE reference LIKE 'AN-T-%' ORDER BY reference"
            ),
            "result_delivery": "inline",
        }
        result = self.call(client, "query_run", query)
        return result["result"]["value"]["rows"]

    def assert_api_refusal(self, message, *extra):
        command = [
            sys.executable,
            "-B",
            "-P",
            "-m",
            API,
            *self.arguments,
            "--role",
            "api",
            *extra,
        ]
        result = subprocess.run(
            command,
            cwd=ENGINE,
            env=self.env,
            input="",
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn(message, result.stderr)
        self.assertFalse((self.directory / "api.sock").exists())

    def peer_ids(self):
        database = self.client("db.sock").get("/health").json()["result"]
        jobs = self.client("jobs.sock").get("/health").json()["result"]
        return database["pid"], jobs["pid"]

    def ready_api(self):
        process = self.start(
            API, "--role", "api", "--blacklist", "query_schema"
        )
        self.wait(
            (self.directory / "api.sock").is_socket,
            process,
            "API did not start",
        )
        client = self.client("api.sock")

        def ready():
            value = client.get("/health").json()
            return (
                value
                if value.get("state") == "ready"
                and not value.get("archive_pending")
                else None
            )

        health = self.wait(
            ready, process, "projection did not settle", timeout=90
        )
        return process, client, health
