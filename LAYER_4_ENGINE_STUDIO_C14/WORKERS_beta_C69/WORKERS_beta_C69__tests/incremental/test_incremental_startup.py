"""Check scoped startup checkpoint reconciliation without a database."""

from ._incremental_cases_0 import IncrementalCases0
from ._incremental_cases_1 import IncrementalCases1
from ._incremental_cases_2 import IncrementalCases2
from .incremental_startup_cases import IncrementalStartupCases
from collections import defaultdict
from hashlib import sha256
import json
import os as os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ..WORKERS_beta_C69__tests__shared import (
    command_with_fixture,
    generation_fixture,
)


WORKER = "WORKERS_beta_C69.WORKERS_beta_C69__shared"


def checkpoint_folders(hashes):
    by_folder = defaultdict(list)
    for path, digest in hashes.items():
        path = Path(path)
        by_folder[path.parent.as_posix()].append((path.name, digest))
    return {
        folder: sha256(
            json.dumps(
                sorted(entries), ensure_ascii=False, separators=(",", ":")
            ).encode()
        ).hexdigest()
        for folder, entries in by_folder.items()
    }


def carrier(number, status="active"):
    return (
        f"---\natom_family: TKT\natom_id: AN-T-{number}\ncontainer: "
        f"{{component: C00}}\npriority: 2\ncontext: {{template: task}}\n"
        f"state: {{status: {status}, version: 1, updated_at: "
        f"'2026-11-22T00:00:00Z'}}\n---\n\n## Summary\n\nTicket "
        f"{number}.\n"
    )


class IncrementalStartupTest(
    IncrementalCases0,
    IncrementalCases1,
    IncrementalCases2,
    IncrementalStartupCases,
    unittest.TestCase,
):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.binding, output, self.manifest = generation_fixture(self.tmp.name)
        declaration = self.manifest.read_text().replace(
            "prefix='AN'))",
            "prefix='AN', parameters={'runtime': {'workbench': "
            "{'import_graph': False}}}))",
        )
        self.manifest.write_text(declaration)
        self.binding["manifest_sha256"] = sha256(
            self.manifest.read_bytes()
        ).hexdigest()
        self.root = Path(self.binding["root"])
        self.control = self.root / self.binding["control_root"]
        self.live = self.control / "__TICKETS"
        self.archive = self.live / "09_archived"
        self.archive.mkdir(parents=True)
        for name, text in (
            ("AN-T-1-task.md", carrier(1)),
            ("AN-T-2-task.md", carrier(2)),
        ):
            (self.live / name).write_text(text)
        (self.archive / "AN-T-8@1-task.md").write_text(carrier(8, "archived"))
        self.roots = [self.archive.relative_to(self.root).as_posix()]
        receipt = self.run_worker(
            output, {"binding": self.binding, "reuse": None}
        )
        hashes = self.checkpoint_hashes()
        self.assertEqual(hashes, receipt["carrier_hashes"])
        self.reuse = receipt["reuse"] | {
            "base_generation": "a" * 64,
            "carrier_hashes": hashes,
            "folder_hashes": checkpoint_folders(hashes),
        }

    def checkpoint_hashes(self):
        return {
            path.relative_to(self.root).as_posix(): sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (self.manifest, *self.live.rglob("*.md"))
        }

    def run_worker(self, output, payload):
        response = command_with_fixture(
            WORKER, payload, "--generation-dir", str(output)
        )
        self.assertEqual(0, response.returncode, response.stderr)
        return json.loads(response.stdout)

    def capture(self, *, archive_roots=None):
        request = {
            "binding": self.binding,
            "reuse": self.reuse,
            "watcher_guarded": True,
            "incremental": True,
        }
        if archive_roots is None:
            request["foreground"] = True
        else:
            request["archive"] = {"roots": archive_roots}
        with TemporaryDirectory(dir=self.tmp.name) as output:
            return self.run_worker(Path(output).resolve(), request)
