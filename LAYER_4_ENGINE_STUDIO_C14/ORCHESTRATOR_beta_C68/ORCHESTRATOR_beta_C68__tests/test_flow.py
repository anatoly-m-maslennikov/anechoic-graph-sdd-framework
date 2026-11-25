"""Exercise generation observations and their private publication."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import Flow, GenerationJobs


class FlowTests(unittest.TestCase):
    def test_generation_events_and_publication(self):
        sent = []
        class Response:
            status = 204
            def read(self):
                return b""
        class Connection:
            def __init__(self, path):
                self.timeout = None
            def request(self, method, path, body, headers):
                sent.append((method, path, json.loads(body), self.timeout))
            def getresponse(self):
                return Response()
            def close(self):
                pass
        with tempfile.TemporaryDirectory() as root:
            binding = {"root": root, "control_root": ".", "manifest_path": "m",
                       "manifest_sha256": "hash", "project_prefix": "AN"}
            jobs = GenerationJobs("id", binding, "socket")
            jobs.flow_context = {"changes": [{"event_type": "modified", "old_path": "/secret"},
                                               {"event_type": "created", "old_path": "/secret2"}],
                                 "retry": True}
            def attempt(*args):
                jobs._flow_effect("generation_admission", outcome="succeeded")
                return {"state": "succeeded"}
            with patch("ORCHESTRATOR_beta_C68.flow.UnixConnection", Connection), \
                    patch.object(jobs, "_attempt_generation", side_effect=attempt):
                self.assertEqual("succeeded", jobs._generate()["state"])
        self.assertEqual(1, len(sent))
        method, path, payload, timeout = sent[0]
        self.assertEqual(("POST", "/flow/events", .5), (method, path, timeout))
        self.assertEqual({"instance_id", "run_id", "component", "action", "events"}, set(payload))
        events = payload["events"]
        self.assertEqual(["file_change", "file_change", "file_change", "retry_due", "retry_due",
                          "generation_reuse_write", "generation_admission", "generation_result"],
                         [event["name"] for event in events])
        self.assertEqual([0, 1], events[2]["causes"])
        self.assertEqual([2, 4, 5, 6], events[-1]["causes"])
        self.assertNotIn("/secret", json.dumps(payload))
        for index, event in enumerate(events):
            self.assertTrue(all(cause < index for cause in event["causes"]))

    def test_watcher_times_survive_queue_and_batch_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            binding = {"root": str(root), "control_root": ".", "manifest_path": "m",
                       "manifest_sha256": "hash", "project_prefix": "AN"}
            jobs = GenerationJobs("id", binding, "socket")
            before = time.time()
            for name in ("one.md", "two.md"):
                jobs.watcher.on_any_event(SimpleNamespace(src_path=str(root / name), dest_path=None,
                                                         event_type="modified", is_directory=False))
            after = time.time()
            self.assertEqual(2, jobs.status()["watcher_queue_depth"])
            changes = jobs.watcher.changes(0)
            self.assertEqual(0, jobs.status()["watcher_queue_depth"])
            self.assertEqual(2, len(changes))
            self.assertTrue(all(before <= change["observed_at"] <= after for change in changes))
            jobs._start_flow(None, changes, False)
            first, second, trigger = jobs.flow.events
            self.assertEqual([change["observed_at"] for change in changes], [first["at"], second["at"]])
            self.assertEqual(["watcher", "watcher"], [first["detail"]["timestamp_source"],
                                                     second["detail"]["timestamp_source"]])
            self.assertEqual([0, 1], trigger["causes"])
            self.assertGreaterEqual(trigger["at"], max(first["at"], second["at"]))

    def test_limit_keeps_terminal_output(self):
        flow = Flow("id", "socket")
        for _ in range(600):
            flow.input("file_change")
        with patch("ORCHESTRATOR_beta_C68.flow.UnixConnection", side_effect=OSError):
            flow.finish({"state": "failed"})
        self.assertEqual("generation_result", flow.events[-1]["name"])
        self.assertGreater(flow.events[-1]["detail"]["omitted_events"], 0)
        self.assertLessEqual(len(flow.events), 512)
