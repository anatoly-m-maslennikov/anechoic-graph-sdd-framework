"""Private lifecycle socket scenarios and fixtures."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from ORCHESTRATOR_beta_C68.lifecycle.lifecycle_queries import lifecycle_context
from ...ORCHESTRATOR_beta_C68__tests__shared import (
    project,
    request_json,
    wait_for,
)


class LifecycleSocketServiceCases:
    def lifecycle_binding(self, root):
        control, manifest = project(root)
        manifest.write_text(
            manifest.read_text().replace(
                "prefix='AN'", "prefix='AN', lens_whitelist=['SPEC']"
            )
        )
        self.write_archived_tickets(control)
        draft_dir = control / "01_draft"
        draft_dir.mkdir(parents=True)
        (
            draft_dir
            / "AN-S-2@1-draft-SPEC-COMPONENT_CONTRACT--admitted-contract.md"
        ).write_text(
            "---\natom_family: SPEC\natom_id: AN-S-2\ncontainer: {component: C00}\ntier: 0\n"
            "context: {template: component_contract, lens: SPEC}\n"
            "state: {status: draft, version: 1, updated_at: '2026-11-23T00:00:00Z'}\n"
            "---\n\n## Summary\n\nAdmitted Contract.\n\n## Guarantee\n\nReturn results.\n",
            encoding="utf-8",
        )
        binding = {
            "root": str(root),
            "control_root": control.name,
            "manifest_path": manifest.name,
            "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
            "project_prefix": "AN",
        }
        (root / "binding.json").write_text(json.dumps(binding))
        return binding

    def test_real_lifecycle_and_generation_admission(self):
        engine = Path(__file__).resolve().parents[4]
        env = {**os.environ, "PYTHONPATH": str(engine)}
        env.setdefault(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(engine.parent / ".anechoic_tmp/workbench/extensions"),
        )
        with tempfile.TemporaryDirectory(
            prefix="ane-lifecycle-admit-", dir="/tmp"
        ) as directory:
            root = Path(directory).resolve()
            binding = self.lifecycle_binding(root)
            db, jobs = str(root / "db.sock"), str(root / "jobs.sock")
            db_module = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"
            jobs_module = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
            database = self._start_lifecycle_database(
                engine, env, db_module, db, binding
            )
            orchestrator = worker = None
            try:
                wait_for(Path(db).exists, database, timeout=10)
                worker = self._start_lifecycle_worker(root, engine, env)
                wait_for((root / "worker.sock").exists, worker, timeout=10)
                orchestrator = self._start_lifecycle_orchestrator(
                    root, engine, env, jobs_module, jobs, db
                )
                wait_for(Path(jobs).exists, orchestrator, timeout=10)
                self.wait_for_archive(db)
                self.assert_lifecycle(jobs, binding, "AN-T-101")
                self.assert_lifecycle(jobs, binding, "AN-T-102")
                self.assert_visible(
                    db,
                    ["AN-S-2@1-draft", "AN-T-101@1-draft", "AN-T-102@1-draft"],
                )
                self.assert_indexed_transitions(jobs, db, binding)
                self.assert_allocation_reserves_quarantined_ids(
                    jobs, db, binding, self.wait_for_archive(db)
                )
            finally:
                for process in (orchestrator, worker, database):
                    if process is not None:
                        process.terminate()
                        process.wait(timeout=10)

    def _start_lifecycle_database(self, engine, env, db_module, db, binding):
        return subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                db_module,
                "--socket",
                db,
                "--instance-id",
                "test",
                "--manifest-sha256",
                binding["manifest_sha256"],
            ],
            cwd=engine,
            env=env,
        )

    def _start_lifecycle_worker(self, root, engine, env):
        return subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                "WORKERS_beta_C69.warm_worker",
                "--socket",
                str(root / "worker.sock"),
            ],
            cwd=engine,
            env=env,
        )

    def _start_lifecycle_orchestrator(
        self, root, engine, env, jobs_module, jobs, db
    ):
        return subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                jobs_module,
                "--socket",
                jobs,
                "--instance-id",
                "test",
                "--binding-file",
                str(root / "binding.json"),
                "--database-socket",
                db,
                "--worker-socket",
                str(root / "worker.sock"),
                "--worker-load-seconds",
                "1",
            ],
            cwd=engine,
            env=env,
        )

    def wait_for_archive(self, path):
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            status, body = request_json(path, "GET", "/health")
            self.assertEqual(200, status, body)
            result = body["result"]
            if result["ready"] and not result["archive_pending"]:
                return result["generation"]
            time.sleep(0.03)
        self.fail("Archive admission did not complete")

    def assert_allocation_reserves_quarantined_ids(
        self, jobs, db, binding, generation
    ):
        issue = {
            "code": "invalid_value",
            "message": "Malformed carrier",
            "related_paths": [],
        }
        inputs = {
            "archive": issue
            | {
                "atom_ref": None,
                "relative_path": "_anechoic_test/__TICKETS/TASKS/09_archived/AN-T-175@1-TASK--bad.md",
            },
            "atom": issue
            | {
                "atom_ref": "AN-S-777@1",
                "relative_path": "_anechoic_test/unreadable.md",
            },
        }
        for source, value in inputs.items():
            payload = {
                "instance_id": "test",
                "source": source,
                "issues": [value],
            }
            status, body = request_json(
                db, "PUT", "/ingestion/issues", payload
            )
            self.assertEqual(
                (200, {"result": {"source": source, "count": 1}}),
                (status, body),
            )
        result = lifecycle_context(
            db,
            "test",
            generation,
            "AN",
            "atom_lifecycle_create_draft",
            {"newAtom": {"template": "task"}},
        )
        self.assertEqual({"T": "175", "S": "777"}, result["max_numbers"])
        self.assert_lifecycle(jobs, binding, "AN-T-176")

    def write_archived_tickets(self, control):
        archive = control / "__TICKETS/TASKS/09_archived"
        archive.mkdir(parents=True)
        for number in ("00099", "100"):
            atom = f"AN-T-{number}"
            (archive / f"{atom}@1-TASK--archived.md").write_text(
                f"---\natom_family: TKT\natom_id: {atom}\ncontainer: {{component: C00}}\n"
                "priority: 2\ncontext: {template: task}\nstate: {status: archived, version: 1, "
                "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\nArchived Task.\n",
                encoding="utf-8",
            )

    def assert_lifecycle(self, path, binding, atom_id):
        result = self.call_lifecycle(
            path,
            binding,
            "create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nLifecycle admission canary.\n",
                }
            },
        )
        self.assertEqual(atom_id, result["savedDraft"]["atom_id"])

    def call_lifecycle(self, path, binding, operation, arguments):
        request = {
            **binding,
            "instance_id": "test",
            "name": "atom_lifecycle_" + operation,
            "arguments": arguments,
        }
        status, result = request_json(
            path, "POST", "/jobs/lifecycle", request, timeout=610
        )
        self.assertEqual(200, status, result)
        self.assertEqual("known", result["result"]["write_state"], result)
        self.assertEqual(
            "completed", result["result"]["lifecycle"]["outcome"], result
        )
        self.assertEqual(
            "ready", result["result"]["projection"]["state"], result
        )
        return result["result"]["lifecycle"]

    def assert_indexed_transitions(self, path, database, binding):
        def call(operation, arguments):
            return self.call_lifecycle(path, binding, operation, arguments)

        task = {"ref_id": "AN-T-101", "version": 1}
        call(
            "promote_draft",
            {
                "target": task | {"ref_id": "AN-T-101@1-draft"},
                "targetStatus": "backlog",
            },
        )
        revision = call("update", {"sourceCurrent": task})["savedDraft"]
        self.assertEqual("AN-T-101@2-draft", revision["ref_id"])
        asset_body = "## Summary\n\nMeasure indexed Ticket Asset.\n"
        asset = call(
            "create_asset",
            {"newAtom": {"template": "work_report", "body": asset_body}},
        )["artifact"]
        call(
            "direct_update",
            {
                "target": {"ref_id": asset["ref_id"], "version": 1},
                "changes": {"body": asset_body + "\nUpdated.\n"},
            },
        )
        draft = call(
            "create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nAdmitted Task.\n",
                }
            },
        )["savedDraft"]
        created_task = {"ref_id": draft["atom_id"], "version": 1}
        call(
            "promote_draft",
            {
                "target": created_task | {"ref_id": draft["ref_id"]},
                "targetStatus": "backlog",
            },
        )
        call("archive", {"target": {"ref_id": "AN-S-2@1-draft", "version": 1}})
        self.assert_visible(database, ["AN-T-101@2-draft", "AN-T-102@1-draft"])

    def assert_visible(self, path, refs):
        sql = "SELECT reference FROM atoms WHERE status_group = 'Draft' ORDER BY reference"
        status, result = request_json(
            path, "POST", "/database", {"instance_id": "test", "sql": sql}
        )
        self.assertEqual(200, status, result)
        self.assertEqual([[ref] for ref in refs], result["result"]["rows"])
