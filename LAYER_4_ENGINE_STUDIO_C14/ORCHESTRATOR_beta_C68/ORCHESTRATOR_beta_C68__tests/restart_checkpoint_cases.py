import json
import subprocess
from unittest.mock import patch


def worker_fixtures(requests):
    class Response:
        status = 200
        header = "old"
        body = b"{}"

        def getheader(self, name):
            return self.header

        def read(self):
            return self.body

    class Connection:
        def __init__(self, path):
            pass

        def request(self, *args):
            pass

        def getresponse(self):
            return response

        def close(self):
            pass

    class Worker:
        returncode = 0

        def __init__(self, *args, **kwargs):
            pass

        def communicate(self, value=None, timeout=None):
            requests.append(json.loads(value))
            return json.dumps(
                {
                    "base_generation": "old",
                    "snapshot": {},
                    "snapshot_sha256": "s",
                }
            ), ""

    response = Response()
    return response, Connection, Worker


class RestartCheckpointCases:
    def test_structure_fallback_for_unavailable_or_invalid_artifact(self):
        jobs = self._jobs("id")
        root = jobs.binding["root"]
        reuse = {"base_generation": "old", "graph_config": {}}
        requests = []

        response, Connection, Worker = worker_fixtures(requests)
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection
            ),
            patch.object(subprocess, "Popen", Worker),
        ):
            jobs._run_worker(str(root), reuse, None)
            self.assertEqual({}, requests[-1]["structure"])
            for status, header, body in (
                (409, "old", b"{}"),
                (200, "other", b"{}"),
                (200, None, b"{}"),
                (200, "old", b"[]"),
                (200, "old", b"{"),
            ):
                response.status, response.header, response.body = (
                    status,
                    header,
                    body,
                )
                jobs._run_worker(str(root), reuse, None)
                self.assertNotIn("structure", requests[-1])
            jobs._run_worker(str(root), reuse | {"graph_config": None}, None)
            self.assertNotIn("structure", requests[-1])
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.UnixConnection",
                side_effect=OSError("offline"),
            ),
            patch.object(subprocess, "Popen", Worker),
        ):
            jobs._run_worker(str(root), reuse, None)
            self.assertNotIn("structure", requests[-1])
