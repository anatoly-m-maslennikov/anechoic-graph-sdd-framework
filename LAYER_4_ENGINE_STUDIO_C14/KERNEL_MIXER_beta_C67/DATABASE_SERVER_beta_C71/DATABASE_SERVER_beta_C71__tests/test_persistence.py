"""Exercise disk storage through the Database Server command and socket."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

import duckdb

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _generation, _launch_arguments, _query, _server


class PersistenceTest(unittest.TestCase):
    def test_restart_binding_and_rollback(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "projection.duckdb"
            data = _generation()
            data["graph"] = {
                "nodes": [["test", "package", "python", "pkg__tests", "ok", None, "Test Package"]],
                "occurrences": [], "edges": [], "test_edges": [["test", "C00"]], "read_issues": [],
            }
            encoded = json.dumps(data["graph"], sort_keys=True, separators=(",", ":"))
            data["receipt"]["graph_sha256"] = sha256(encoded.encode()).hexdigest()
            with _server(path) as client:
                response = client.put("/generation", json=data)
                self.assertEqual(200, response.status_code, response.text)
                generation = response.json()["result"]["generation"]
                bad = deepcopy(data)
                bad["snapshot"]["atoms"] *= 2
                self.assertEqual(400, client.put("/generation", json=bad).status_code)
            self.assertEqual(0, path.stat().st_mode & 0o077)
            raw = duckdb.connect(str(path))
            raw.execute("DROP TABLE mrt_diag_state_effects")
            raw.close()
            self.assert_rejected(path, "different Project manifest", pin="c" * 64)
            self.assert_rejected(path, "different Project manifest", instance="foreign")
            with _server(path) as client:
                self.assertEqual(generation, client.get("/health").json()["result"]["generation"])
                self.assertEqual(data["model"], client.get("/model", params=BINDING).text)
                self.assertEqual(json.loads(data["structure"]), client.get("/structure", params=BINDING).json())
                self.assertEqual([["one", "first"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])
                self.assertEqual([], _query(client, "SELECT * FROM state_effect_findings").json()["result"]["rows"])
                graph = _query(client, "FROM GRAPH_TABLE (anechoic MATCH (n:Reference)-[e:COMPONENT_IS_TESTED_BY]->"
                                       "(t:ImportNode) COLUMNS (n.ref AS ref, t.node_key AS test))")
                self.assertEqual(200, graph.status_code, graph.text)
                self.assertEqual([["C00", "test"]], graph.json()["result"]["rows"])

    def test_reject_unsafe_paths(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            parent = Path(directory).resolve()
            self.assert_rejected(Path("relative.duckdb"), "Database path must be absolute")
            unsafe = parent / "unsafe"
            unsafe.mkdir(mode=0o755)
            self.assert_rejected(unsafe / "db", "Database directory is unavailable or unsafe")
            unbound = parent / "unbound.duckdb"
            raw = duckdb.connect(str(unbound))
            raw.execute("CREATE TABLE old_data (value INTEGER)")
            raw.close()
            unbound.chmod(0o600)
            self.assert_rejected(unbound, "Database has no Project binding")
            link = parent / "link"
            link.symlink_to(unbound)
            self.assert_rejected(link, "Database file is unavailable or unsafe")

    def assert_rejected(self, path, error, pin=PIN, instance="instance"):
        with TemporaryDirectory(prefix="ane-db-reject-", dir="/tmp") as directory:
            socket = Path(directory).resolve() / "db.sock"
            command, env = _launch_arguments(socket, path, pin, instance)
            result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(0, result.returncode)
            self.assertIn(error, result.stderr)
            self.assertFalse(socket.exists())
