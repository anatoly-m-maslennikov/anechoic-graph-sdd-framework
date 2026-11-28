"""Restart checkpoint test cases."""

import json
from pathlib import Path
import subprocess
from unittest.mock import patch

from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.restart_checkpoint_test_support import _reuse_connection


def _graph_connection(calls):
    class Response:
        status = 200

        def getheader(self, name):
            return "old"

        def read(self):
            return (
                b'{"result": {"generation": "new"}}'
                if calls[-1][0] == "PUT"
                else b'{"nodes": []}'
            )

    class Connection:
        def __init__(self, path):
            pass

        def request(self, method, path, body=None, headers=None):
            calls.append((method, path, json.loads(body) if body else None))

        def getresponse(self):
            return Response()

        def close(self):
            pass

    return Connection


class RestartGraphCases:
    def test_scoped_request_never_falls_back_to_full_checkpoint(self):
        calls = []
        result = {
            "base_generation": "old",
            "inputs": {},
            "graph_config": None,
            "endpoints": {},
        }

        class Connection:
            def __init__(self, path):
                pass

            def request(self, method, path):
                calls.append(path)

            def getresponse(self):
                class Response:
                    status = 403 if len(calls) == 1 else 200

                    def read(self):
                        return json.dumps({"result": result}).encode()

                return Response()

            def close(self):
                pass

        with patch(
            "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
        ):
            self.assertIsNone(
                module.read_reuse("socket", "test", scope="foreground")
            )
            self.assertIsNone(
                module.read_reuse("socket", "test", scope="foreground")
            )
        self.assertEqual(
            ["/generation/reuse?instance_id=test&scope=foreground"] * 2, calls
        )

    def test_full_admission_persists_worker_witness(self):
        jobs = self._jobs()
        witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
        payloads = []

        class Connection:
            def __init__(self, path):
                pass

            def request(self, method, path, body, headers):
                payloads.append((path, json.loads(body)))

            def getresponse(self):
                class Response:
                    status = 200

                    def read(self):
                        return b'{"result": {"generation": "new"}}'

                return Response()

            def close(self):
                pass

        def worker(directory, reuse, paths, *, force_model=False):
            self.assertFalse(force_model)
            for name in ("model", "structure"):
                (Path(directory) / (name + ".json")).write_text("{}")
            return {
                "snapshot": {},
                "receipt": {},
                "graph": None,
                "reuse": witness,
                "model_diagnostics": [],
                "carrier_hashes": {"control/a.md": "a" * 64},
            }

        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
            ),
            patch.object(jobs, "_run_worker", side_effect=worker),
        ):
            self.assertEqual(
                "full", jobs._attempt_generation(None, None)["kind"]
            )
        self.assertEqual("/generation", payloads[0][0])
        self.assertEqual(witness, payloads[0][1]["reuse"])
        self.assertEqual([], payloads[0][1]["model_diagnostics"])
        self.assertEqual(
            {"control/a.md": "a" * 64}, payloads[0][1]["carrier_hashes"]
        )

    def test_graph_refresh_request_validation_and_admission(self):
        from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.test_restart_checkpoint import graph_worker

        jobs = self._jobs("test id")
        witness = {"inputs": {}, "graph_config": {}, "endpoints": {}}
        reuse = {**witness, "base_generation": "old"}
        graph_result = {
            "base_generation": "old",
            "snapshot": {},
            "snapshot_sha256": "s",
            "graph": {},
            "graph_sha256": "g",
            "reuse": witness,
        }
        calls = []

        Connection = _graph_connection(calls)

        requests = []
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
            ),
            patch.object(
                subprocess, "Popen", graph_worker(graph_result, requests)
            ),
        ):
            outcome = jobs._attempt_generation(None, reuse)
        self._assert_graph_request(
            jobs, reuse, witness, requests, calls, outcome
        )

    def _assert_graph_request(
        self, jobs, reuse, witness, requests, calls, outcome
    ):
        self.assertEqual(
            {
                "binding": jobs.binding,
                "reuse": reuse,
                "structure": {"nodes": []},
                "model_source": {
                    "accepted_model": None,
                    "spec_database": {
                        "socket": str(jobs.database_socket),
                        "instance_id": "test id",
                    },
                },
                "batch_full": True,
            },
            requests[0],
        )
        self.assertEqual(
            ("GET", "/structure?instance_id=test+id"), calls[0][:2]
        )
        self.assertEqual("/generation/native", calls[1][1])
        self.assertEqual(
            {
                "instance_id",
                "base_generation",
                "snapshot",
                "snapshot_sha256",
                "graph",
                "graph_sha256",
                "reuse",
            },
            set(calls[1][2]),
        )
        self.assertEqual("graph_refresh", outcome["kind"])
        self.assertEqual(
            {**witness, "base_generation": "new"},
            jobs.generation_reuse.model_dump(exclude_unset=True),
        )
        self.assertEqual(witness, calls[1][2]["reuse"])

    def test_unchanged_confirms_base_and_drops_checkpoint(self):
        jobs = self._jobs()
        reuse = {
            "base_generation": "old",
            "inputs": {},
            "graph_config": None,
            "endpoints": {},
            "carrier_hashes": {"control/a.md": "a" * 64},
        }
        calls = []

        Connection = _reuse_connection(reuse, calls)

        result = {"base_generation": "old", "unchanged": True}
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
            ),
            patch.object(jobs, "_record_ingestion_issues"),
            patch.object(jobs, "_run_worker", return_value=result),
        ):
            outcome = jobs._attempt_generation(None, reuse)
        self.assertEqual("reused", outcome["kind"])
        self.assertEqual(
            [("GET", "/generation/reuse?instance_id=test")], calls
        )
        self.assertNotIn("carrier_hashes", jobs.generation_reuse)
        reuse["base_generation"] = "new"
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
            ),
            patch.object(jobs, "_run_worker", return_value=result),
        ):
            with self.assertRaises(module.GenerationBaseChanged):
                jobs._attempt_generation(None, reuse)
