from hashlib import sha256
from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[3]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.native_lifecycle_update_support import (
    NativeUpdateSupport,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.updates import (  # noqa: E402
    _native_lifecycle_status_cases as cases,
)


class NativeDirectUpdateTests(
    cases.NativeLifecycleStatusCases, NativeUpdateSupport, unittest.TestCase
):
    def _write_ticket(self, relative, identity, container, template, status):
        path = self.write(relative, identity)
        body = path.read_text().split("---\n", 2)[2]
        header = {
            "atom_family": "TKT",
            "atom_id": identity,
            "container": container,
            "priority": 2,
            "context": {"template": template, "label": template.title()},
            "state": {
                "status": status,
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n" + body)
        return path

    def _triage_domains(self):
        return {
            "S": {"draft", "ready", "active", "archived"},
            "T": {
                "draft",
                "backlog",
                "in_queue",
                "done",
                "canceled",
                "archived",
                "triage",
            },
            "P": {"draft", "active", "archived"},
            "C": {"draft", "active", "archived"},
        }

    def test_project_current_status_uses_admitted_ticket_domain(self):
        self.path.unlink()
        path = self._write_ticket(
            "001_TICKETS/TASKS/backlog/AN-T-1-TASK--example.md",
            "AN-T-1",
            {"component": "C0"},
            "task",
            "backlog",
        )
        domains = self._triage_domains()
        capture = capture_native(self.selection, domains=domains)
        target = self.params["target"]
        with self.assertRaises(InputError):
            change_ticket_status(
                self.selection,
                {"target": target, "targetStatus": "unknown"},
                current_rows=capture.atoms,
                previous_capture=capture,
                check_definition=lambda: None,
            )
        outcome = change_ticket_status(
            self.selection,
            {"target": target, "targetStatus": "triage"},
            current_rows=capture.atoms,
            previous_capture=capture,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", outcome["outcome"])
        self.assertFalse(path.exists())
        capture = capture_native(self.selection, domains=domains)
        row = next(row for row in capture.atoms if row["id"] == "AN-T-1")
        self.assertEqual(
            ("Current", "triage", 1),
            (row["status_group"], row["status"], row["version"]),
        )
        outcome = change_ticket_status(
            self.selection,
            {"target": target, "targetStatus": "in_queue"},
            current_rows=capture.atoms,
            previous_capture=capture,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", outcome["outcome"])
        self.assertTrue((path.parent.parent / path.name).exists())

    def test_project_current_status_is_retained_during_cascade_reads(self):
        self.path.unlink()
        epic = self._write_ticket(
            "001_TICKETS/TASKS/AN-T-1-EPIC--example.md",
            "AN-T-1",
            {"component": "C0"},
            "epic",
            "in_queue",
        )
        self._write_ticket(
            "001_TICKETS/TASKS/"
            + epic.stem
            + "/triage/AN-T-2-TASK--example.md",
            "AN-T-2",
            {"atom": "AN-T-1"},
            "task",
            "triage",
        )
        domains = self._triage_domains()
        capture = capture_native(self.selection, domains=domains)
        result = change_ticket_status(
            self.selection,
            {"target": self.params["target"], "targetStatus": "canceled"},
            current_rows=capture.atoms,
            previous_capture=capture,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", result["outcome"])
        rows = capture_native(self.selection, domains=domains).atoms
        self.assertEqual(
            {"AN-T-1": "canceled", "AN-T-2": "canceled"},
            {
                row["id"]: row["status"]
                for row in rows
                if row["id"].startswith("AN-T-")
            },
        )

    def test_status_moves_and_preserves_body_and_identity(self):
        before = self.path.read_bytes()
        checks = []
        params = {"target": self.params["target"], "targetStatus": "Done"}
        output = change_ticket_status(
            self.selection,
            params,
            current_rows=self.rows,
            check_definition=lambda: checks.append(True),
        )
        destination = self.path.parent / "done" / self.path.name
        self.assertEqual("completed", output["outcome"])
        self.assertEqual(
            ["create", "create", "remove"],
            [item["operation"] for item in output["effects"]],
        )
        self.assertEqual(3, len(checks))
        self.assertFalse(self.path.exists())
        self.assertEqual(
            before.split(b"---\n", 2)[2],
            destination.read_bytes().split(b"---\n", 2)[2],
        )
        parsed = yaml.safe_load(destination.read_text().split("---\n", 2)[1])
        self.assertEqual(
            ("AN-T-1", 1, "done"),
            (
                parsed["identity"]["atom_id"],
                parsed["state"]["version"],
                parsed["state"]["status"],
            ),
        )
        self.assertNotEqual(
            "2026-11-19T00:00:00Z", parsed["state"]["updated_at"]
        )
        self.assertEqual(
            destination.relative_to(self.root).as_posix(),
            output["artifact"]["path"],
        )
        self._assert_status_reopened(destination)

    def _assert_status_reopened(self, destination):
        rows = capture_native(self.selection).atoms
        for row in rows:
            row["_source_sha256"] = sha256(
                (self.root / row["source_path"]).read_bytes()
            ).hexdigest()
        reopened = change_ticket_status(
            self.selection,
            {"target": self.params["target"], "targetStatus": "in_queue"},
            current_rows=rows,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", reopened["outcome"])
        self.assertTrue(self.path.exists())
        self.assertFalse(destination.exists())

    def test_status_uses_each_branch_and_current_status_folder(self):
        for number, (branch, status) in enumerate(
            (
                ("TASKS", "backlog"),
                ("ISSUES", "resolved"),
                ("ASSETS", "canceled"),
            ),
            2,
        ):
            identity = f"AN-T-{number}"
            path = self.write(
                f"001_TICKETS/{branch}/{identity}-TICKET--example.md", identity
            )
            rows = capture_native(self.selection).atoms
            for row in rows:
                row["_source_sha256"] = sha256(
                    (self.root / row["source_path"]).read_bytes()
                ).hexdigest()
            outcome = change_ticket_status(
                self.selection,
                {
                    "target": {"ref_id": identity, "version": 1},
                    "targetStatus": status,
                },
                current_rows=rows,
                check_definition=lambda: None,
            )
            self.assertEqual("completed", outcome["outcome"])
            self.assertTrue((path.parent / status / path.name).is_file())
            self.assertFalse(path.exists())

    def test_status_collision_and_definition_failure_preserve_source(self):
        params = {"target": self.params["target"], "targetStatus": "done"}
        original = self.path.read_bytes()
        destination = self.path.parent / "done" / self.path.name
        destination.parent.mkdir()
        destination.write_bytes(b"occupied")
        outcome = change_ticket_status(
            self.selection,
            params,
            current_rows=self.rows,
            check_definition=lambda: None,
        )
        self.assertEqual("failed", outcome["outcome"])
        self.assertEqual([], outcome["effects"])
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(b"occupied", destination.read_bytes())
        destination.unlink()
        calls = []

        def check():
            calls.append(True)
            if len(calls) == 2:
                raise ValueError("definition changed")

        outcome = change_ticket_status(
            self.selection,
            params,
            current_rows=self.rows,
            check_definition=check,
        )
        self.assertEqual("failed", outcome["outcome"])
        self.assertEqual(
            ["create", "remove"],
            [effect["operation"] for effect in outcome["effects"]],
        )
        self.assertEqual(
            "definition_revalidation_required", outcome["errors"][0]["code"]
        )
        self.assertEqual(original, self.path.read_bytes())
        self.assertFalse(destination.exists())
