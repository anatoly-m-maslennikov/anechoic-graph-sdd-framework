"""Git fixture and CLI helper for public release tests."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared import (
    run_public_release,
)


class PublicReleaseFixture:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "version.toml").write_text(
            '[framework]\nversion = "1.2.3"\n'
        )
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD")
        (self.root / "version.toml").write_text(
            '[framework]\nversion = "1.2.4"\n'
        )
        self.tickets = self.root / "_anechoic_anechoic/001_TICKETS/TASKS"
        self.tickets.mkdir(parents=True)
        (self.tickets / "AN-T-1-TASK--done.md").write_text(
            (
                "---\natom_id: AN-T-1\ncontext:\n  template: task\nstate:\n  "
                'status: "done"\n---\n# Summary\n\nDone task\n'
            )
        )
        (self.tickets / "AN-T-2-EPIC--open.md").write_text(
            (
                "---\natom_id: AN-T-2\ncontext:\n  template: epic\nstate:\n  "
                "status: active\n---\n"
            )
        )
        for branch, number in (("__TICKETS", 3), ("__TKT", 4)):
            directory = self.root / "_anechoic_anechoic" / branch / "TASKS"
            directory.mkdir(parents=True)
            (directory / f"AN-T-{number}-TASK--done.md").write_text(
                (
                    "---\natom_id: AN-T-"
                    f"{number}"
                    "\ncontext:\n  template: task\nstate:\n  status: "
                    "done\n---\n"
                )
            )
        self.git("add", ".")
        self.git("commit", "-qm", "head")
        self.head = self.git("rev-parse", "HEAD")
        self.addCleanup(self.tmp.cleanup)

    def git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def run_release(self, **kwargs):
        return run_public_release(
            self.root,
            run_id="test",
            base_ref=self.base,
            head_ref=self.head,
            **kwargs,
        )

    def run_cli(self, *arguments):
        release = Path(__file__).resolve().parents[2] / "release.py"
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(release),
                "public",
                "--project-root",
                str(self.root),
                "--run-id",
                "test",
                "--base",
                self.base,
                "--head",
                self.head,
                *arguments,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(1, len(result.stdout.splitlines()), result.stdout)
        return result.returncode, json.loads(result.stdout)
