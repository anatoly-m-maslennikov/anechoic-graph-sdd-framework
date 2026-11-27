"""Check scoped startup checkpoint reconciliation without a database."""
from .incremental_startup_cases import IncrementalStartupCases
from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .WORKERS_beta_C69__tests__shared import command_with_fixture, generation_fixture


WORKER = "WORKERS_beta_C69.WORKERS_beta_C69__shared"


def checkpoint_folders(hashes):
    by_folder = defaultdict(list)
    for path, digest in hashes.items():
        path = Path(path)
        by_folder[path.parent.as_posix()].append((path.name, digest))
    return {folder: sha256(json.dumps(sorted(entries), ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            for folder, entries in by_folder.items()}


def carrier(number, status="active"):
    return (f"---\natom_family: TKT\natom_id: AN-T-{number}\ncontainer: {{component: C00}}\npriority: 2\ncontext: {{template: task}}\n"
            f"state: {{status: {status}, version: 1, updated_at: '2026-11-22T00:00:00Z'}}\n---\n\n## Summary\n\nTicket {number}.\n")


class IncrementalStartupTest(IncrementalStartupCases, unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.binding, output, self.manifest = generation_fixture(self.tmp.name)
        declaration = self.manifest.read_text().replace("prefix='AN'))",
            "prefix='AN', parameters={'runtime': {'workbench': {'import_graph': False}}}))")
        self.manifest.write_text(declaration)
        self.binding["manifest_sha256"] = sha256(self.manifest.read_bytes()).hexdigest()
        self.root = Path(self.binding["root"])
        self.control = self.root / self.binding["control_root"]
        self.live = self.control / "__TICKETS"
        self.archive = self.live / "09_archived"
        self.archive.mkdir(parents=True)
        for name, text in (("AN-T-1-task.md", carrier(1)), ("AN-T-2-task.md", carrier(2))):
            (self.live / name).write_text(text)
        (self.archive / "AN-T-8@1-task.md").write_text(carrier(8, "archived"))
        self.roots = [self.archive.relative_to(self.root).as_posix()]
        receipt = self.run_worker(output, {"binding": self.binding, "reuse": None})
        hashes = self.checkpoint_hashes()
        self.assertEqual(hashes, receipt["carrier_hashes"])
        self.reuse = receipt["reuse"] | {"base_generation": "a" * 64, "carrier_hashes": hashes,
                                         "folder_hashes": checkpoint_folders(hashes)}

    def checkpoint_hashes(self):
        return {path.relative_to(self.root).as_posix(): sha256(path.read_bytes()).hexdigest()
                for path in (self.manifest, *self.live.rglob("*.md"))}

    def run_worker(self, output, payload):
        response = command_with_fixture(WORKER, payload, "--generation-dir", str(output))
        self.assertEqual(0, response.returncode, response.stderr)
        return json.loads(response.stdout)

    def capture(self, *, archive_roots=None):
        request = {"binding": self.binding, "reuse": self.reuse, "watcher_guarded": True, "incremental": True}
        if archive_roots is None:
            request["foreground"] = True
        else:
            request["archive"] = {"roots": archive_roots}
        with TemporaryDirectory(dir=self.tmp.name) as output:
            return self.run_worker(Path(output).resolve(), request)

    def test_incremental_capture_uses_admitted_status_domains(self):
        self.reuse["status_domains"] = {
            "S": ["active", "draft", "archived"], "T": ["active", "draft", "archived", "reviewed"],
            "P": ["active", "draft", "archived"], "C": ["active", "draft", "archived"],
        }
        (self.live / "AN-T-3-task.md").write_text(carrier(3, "reviewed"))
        (self.live / "AN-T-4-task.md").write_text(carrier(4, "unknown"))
        result = self.capture()
        row = next(row for row in result["snapshot"]["atoms"] if row["reference"] == "AN-T-3")
        self.assertEqual(("reviewed", "Current"), (row["status"], row["status_group"]))
        self.assertTrue(any(issue["relative_path"].endswith("AN-T-4-task.md")
                            for issue in result["snapshot"]["ingestion_issues"]))

    def test_watcher_replay_requires_managed_foreground_without_explicit_paths(self):
        base = {"binding": {}, "reuse": None, "replay_graph": True,
                "watcher_guarded": True, "foreground": True}
        replay = "Graph replay requires a watcher-guarded foreground capture"
        fields = "Invalid managed Worker fields"
        option = "Invalid managed Worker option"
        invalid = (({"watcher_guarded": False}, replay), ({"foreground": False}, replay),
                   ({"paths": []}, replay), ({"archive": {}}, replay), ({"unexpected": True}, replay),
                   ({"archive": None, "paths": None}, replay), ({"replay_graph": False, "paths": None, "structure": None}, fields),
                   ({"replay_graph": False, "unexpected": True}, fields),
                   *(({flag: 1, "unexpected": True}, option)
                     for flag in ("watcher_guarded", "foreground", "incremental", "replay_graph", "defer_graph", "graph_only")))
        for options, message in invalid:
            with self.subTest(options=options):
                response = command_with_fixture(WORKER, base | options, "--generation-dir", "/fixture")
                self.assertEqual(1, response.returncode)
                issue, = json.loads(response.stdout)["ingestion_failure"]["issues"]
                self.assertEqual(message, issue["message"])

    def test_deferred_warm_start_ignores_graph_input_changes(self):
        self.reuse["graph_config"] = {"include": []}
        self.reuse["inputs"]["graph"] = "old-graph-signature"
        (self.root / "changed.py").write_text("value = 1\n")
        request = {"binding": self.binding, "reuse": self.reuse, "watcher_guarded": True,
                   "incremental": True, "foreground": True, "defer_graph": True}
        signature = "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared.graph_input_signature"
        with (patch(signature, side_effect=AssertionError("graph scanned")),
              patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}),
              TemporaryDirectory(dir=self.tmp.name) as output):
            response = command_with_fixture(WORKER, request, "--generation-dir", str(Path(output).resolve()))
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, json.loads(response.stdout))
        self.assertIn('"mode":"reused","phase":"model_ready"', response.stderr)
        self.assertIn('"mode":"reused","phase":"structure_ready"', response.stderr)
        self.assertNotIn("realization_graph_ready", response.stderr)

    def test_timing_reports_compilation_and_checkpoint_reuse(self):
        def events(response):
            prefix = "ANECHOIC_STARTUP_TIMING "
            return [json.loads(line[len(prefix):]) for line in response.stderr.splitlines() if line.startswith(prefix)]

        with patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}):
            with TemporaryDirectory(dir=self.tmp.name) as output:
                cold = command_with_fixture(WORKER, {"binding": self.binding, "reuse": None, "foreground": True, "defer_graph": True},
                                            "--generation-dir", str(Path(output).resolve()))
            self.assertEqual(0, cold.returncode, cold.stderr)
            modes = {event["phase"]: event.get("mode") for event in events(cold)}
            self.assertEqual("built", modes["model_ready"])
            self.assertEqual("built", modes["structure_ready"])
            self.assertEqual("disabled", modes["realization_graph_ready"])
            self.assertIn("non_archived_load_started", modes)
            request = {"binding": self.binding, "reuse": self.reuse, "watcher_guarded": True,
                       "incremental": True, "foreground": True}
            with TemporaryDirectory(dir=self.tmp.name) as output:
                warm = command_with_fixture(WORKER, request, "--generation-dir", str(Path(output).resolve()))
            self.assertEqual(0, warm.returncode, warm.stderr)
            self.assertTrue(json.loads(warm.stdout)["unchanged"])
            by_phase = {event["phase"]: event for event in events(warm)}
            self.assertEqual("reused", by_phase["model_ready"]["mode"])
            self.assertEqual("reused", by_phase["structure_ready"]["mode"])
            self.assertEqual("disabled", by_phase["realization_graph_ready"]["mode"])
            self.assertEqual(0, by_phase["non_archived_load_started"]["changed_paths"])
            self.assertGreaterEqual(by_phase["non_archived_load_started"]["comparison_ns"], 0)
            self.assertGreaterEqual(by_phase["non_archived_load_started"]["checkpoint_validation_ns"], 0)

    def test_rejected_checkpoint_does_not_report_reuse(self):
        self.reuse["folder_hashes"] = {}
        request = {"binding": self.binding, "reuse": self.reuse, "watcher_guarded": True,
                   "incremental": True, "foreground": True}
        with patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}), TemporaryDirectory(dir=self.tmp.name) as output:
            response = command_with_fixture(WORKER, request, "--generation-dir", str(Path(output).resolve()))
        self.assertEqual(0, response.returncode, response.stderr)
        self.assertIn("receipt", json.loads(response.stdout))
        prefix = "ANECHOIC_STARTUP_TIMING "
        events = [json.loads(line[len(prefix):]) for line in response.stderr.splitlines() if line.startswith(prefix)]
        milestones = [event for event in events if event["phase"] in {
            "model_ready", "structure_ready", "realization_graph_ready"}]
        self.assertTrue(milestones)
        self.assertNotIn("reused", [event.get("mode") for event in milestones])

    def test_foreground_unchanged_and_offline_add_edit_move_delete(self):
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, self.capture())
        first = self.live / "AN-T-1-task.md"
        stamp = first.stat()
        first.write_text(first.read_text().replace("Ticket 1.", "Ticket X."))
        os.utime(first, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        second = self.live / "AN-T-2-task.md"
        moved = self.live / "AN-T-2-moved.md"
        second.rename(moved)
        added = self.live / "AN-T-3-task.md"
        added.write_text(carrier(3))
        result = self.capture()
        paths = {str(Path(parent) / name) for parent, name in result["paths"]}
        self.assertEqual({p.relative_to(self.root).as_posix() for p in (first, second, moved, added)}, paths)
        self.assertEqual({p.relative_to(self.root).as_posix() for p in (first, moved, added)}, set(result["carrier_hashes"]))
        self.assertEqual(3, len(result["snapshot"]["atoms"]))

    def test_addressed_delta_captures_only_the_named_ticket(self):
        first = self.live / "AN-T-1-task.md"
        second = self.live / "AN-T-2-task.md"
        first.write_text(first.read_text().replace("Ticket 1.", "Ticket X."))
        second.write_text(second.read_text().replace("Ticket 2.", "Ticket Y."))
        relative = first.relative_to(self.root).as_posix()
        deferred_reuse = self.reuse | {"graph_config": {}, "inputs": self.reuse["inputs"] | {"graph": "pending"}}
        request = {"binding": self.binding, "watcher_guarded": True, "paths": [relative]}
        for mode, reuse in (("foreground", self.reuse), ("defer_graph", deferred_reuse)):
            with self.subTest(mode=mode), TemporaryDirectory(dir=self.tmp.name) as output:
                result = self.run_worker(Path(output).resolve(), request | {mode: True, "reuse": reuse})
                self.assertEqual(reuse["base_generation"], result.get("base_generation"))
                self.assertEqual([[first.parent.relative_to(self.root).as_posix(), first.name]], result["paths"])
                self.assertEqual({relative: sha256(first.read_bytes()).hexdigest()}, result["carrier_hashes"])
                self.assertEqual(["AN-T-1"], [row["reference"] for row in result["snapshot"]["atoms"]])
                self.assertEqual([], list(Path(output).iterdir()))

    def test_archive_unchanged_move_and_delete(self):
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, self.capture(archive_roots=self.roots))
        original = self.archive / "AN-T-8@1-task.md"
        moved = self.archive / "AN-T-8@1-moved.md"
        original.rename(moved)
        result = self.capture(archive_roots=self.roots)
        self.assertEqual({original.name, moved.name}, {row[1] for row in result["paths"]})
        self.assertEqual(["Archived"], [row["status_group"] for row in result["snapshot"]["atoms"]])
        moved.unlink()
        self.assertEqual({}, self.capture(archive_roots=self.roots)["carrier_hashes"])

    def test_full_archive_checks_roots_and_keeps_foreground_out(self):
        archive = {"roots": self.roots, "endpoints": self.reuse["endpoints"]}
        request = {"binding": self.binding, "reuse": None, "watcher_guarded": True, "archive": archive}
        with TemporaryDirectory(dir=self.tmp.name) as output:
            result = self.run_worker(Path(output).resolve(), request)
            self.assertEqual({"snapshot", "carrier_hashes"}, set(result))
            self.assertEqual(["AN-T-8@1"], [row["reference"] for row in result["snapshot"]["atoms"]])
            self.assertEqual({f"{self.roots[0]}/AN-T-8@1-task.md"}, set(result["carrier_hashes"]))
            self.assertEqual([], list(Path(output).iterdir()))
            invalid = request | {"archive": archive | {"roots": [self.live.relative_to(self.root).as_posix()]}}
            response = command_with_fixture(WORKER, invalid, "--generation-dir", output)
            self.assertEqual(1, response.returncode, response.stderr)
            issue, = json.loads(response.stdout)["ingestion_failure"]["issues"]
            self.assertEqual("Deferred archive directory is outside the selected native archive trees", issue["message"])
            self.assertEqual([], list(Path(output).iterdir()))

    def test_incompatible_checkpoint_falls_back(self):
        self.reuse["folder_hashes"] = {}
        self.assertIn("receipt", self.capture())
        self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))


    def test_archive_delta_excludes_wrong_status_and_keeps_valid_rows(self):
        invalid = self.archive / "AN-T-9-task.md"
        valid = self.archive / "AN-T-10@1-task.md"
        invalid.write_text(carrier(9))
        valid.write_text(carrier(10, "archived"))
        result = self.capture(archive_roots=self.roots)
        snapshot = result["snapshot"]
        self.assertEqual([(valid.name, "Archived")], [
            (row["filename"], row["status_group"]) for row in snapshot["atoms"]])
        relative = invalid.relative_to(self.root).as_posix()
        self.assertEqual([relative], [issue["relative_path"] for issue in snapshot["ingestion_issues"]])
        self.assertEqual(sha256(invalid.read_bytes()).hexdigest(), result["carrier_hashes"][relative])

    def test_legacy_delta_falls_back_and_malformed_carrier_is_reported(self):
        live = self.live / "AN-T-1-task.md"
        live.write_text("---\nidentity: {atom_id: AN-T-1}\ncontext: {container: {component: C00}}\n"
                        "state: {status: active, version: 1}\n---\n\n## Summary\n\nLegacy.\n")
        hashes = self.checkpoint_hashes()
        self.reuse.update(carrier_hashes=hashes, folder_hashes=checkpoint_folders(hashes))
        live.write_text(live.read_text().replace("Legacy.", "Changed."))
        self.assertIn("receipt", self.capture())
        live.write_text("---\ninvalid: [\n---\n")
        result = self.capture()
        relative = live.relative_to(self.root).as_posix()
        self.assertEqual([], result["snapshot"]["atoms"])
        self.assertEqual([relative], [issue["relative_path"] for issue in result["snapshot"]["ingestion_issues"]])
        self.assertEqual(sha256(live.read_bytes()).hexdigest(), result["carrier_hashes"][relative])

    def test_schema_and_large_diff_require_reconciliation(self):
        schema = self.reuse["inputs"].pop("carrier_schema")
        self.assertIn("receipt", self.capture())
        self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))
        self.reuse["inputs"]["carrier_schema"] = schema
        many = {f"{self.binding['control_root']}/__TICKETS/AN-T-{i}-task.md": "c" * 64 for i in range(2000, 3025)}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.native_carrier_hashes",
                   return_value=many):
            self.assertIn("receipt", self.capture())
            self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))

    def test_folder_hashes_are_canonical_and_validate_paths(self):
        (self.live / "AN-T-4--состояние.md").write_text(carrier(4))
        values = self.checkpoint_hashes()
        self.reuse["folder_hashes"] = checkpoint_folders(values)
        self.reuse["carrier_hashes"] = dict(reversed(list(values.items())))
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, self.capture())
        self.reuse["carrier_hashes"] = values | {"../escape.md": "c" * 64}
        self.reuse["folder_hashes"] = checkpoint_folders(self.reuse["carrier_hashes"])
        self.assertIn("receipt", self.capture())
        self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))

    def test_current_inventory_rejects_literal_backslash(self):
        (self.live / "AN-T-4-invalid\\name.md").write_text(carrier(4))
        request = {"binding": self.binding, "reuse": self.reuse, "watcher_guarded": True,
                   "incremental": True, "foreground": True}
        with TemporaryDirectory(dir=self.tmp.name) as output:
            response = command_with_fixture(WORKER, request, "--generation-dir", output)
            self.assertEqual(1, response.returncode, response.stderr)
            issue, = json.loads(response.stdout)["ingestion_failure"]["issues"]
            self.assertEqual("Invalid carrier checkpoint path", issue["message"])
            self.assertFalse(any(Path(output).iterdir()))


class ForegroundReplayGraphTest(unittest.TestCase):
    def test_graph_refresh_checks_archives_outside_foreground_watcher(self):
        directory = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding, output, _ = generation_fixture(directory)
        root = Path(binding["root"])
        archived = root / binding["control_root"] / "__TICKETS" / "09_archived" / "AN-T-8@1-task.md"
        archived.parent.mkdir(parents=True)
        archived.write_text(carrier(8, "archived"))
        full = command_with_fixture(WORKER, {"binding": binding, "reuse": None}, "--generation-dir", str(output))
        self.assertEqual(0, full.returncode, full.stderr)
        reuse = json.loads(full.stdout)["reuse"] | {"base_generation": "admitted"}
        structure = json.loads((output / "structure.json").read_text())
        (root / "source.py").write_text("VALUE = 1\n")
        output = directory / "refresh"
        output.mkdir()
        original = subprocess.run

        def graph_with_archive_edit(command, *args, **options):
            if "WORKERS_beta_C69.realization_graph" in command:
                archived.write_text(carrier(8, "archived").replace("Ticket 8.", "Edited archive."))
            return original(command, *args, **options)

        request = {"binding": binding, "reuse": reuse, "foreground": True, "incremental": True,
                   "watcher_guarded": True, "structure": structure}
        with patch.object(subprocess, "run", side_effect=graph_with_archive_edit):
            result = command_with_fixture(WORKER, request, "--generation-dir", str(output))
        self.assertEqual(1, result.returncode, result.stdout)
        issue, = json.loads(result.stdout)["ingestion_failure"]["issues"]
        self.assertIn("Native Project carriers changed during generation", issue["message"])
        self.assertFalse(any(output.iterdir()))
