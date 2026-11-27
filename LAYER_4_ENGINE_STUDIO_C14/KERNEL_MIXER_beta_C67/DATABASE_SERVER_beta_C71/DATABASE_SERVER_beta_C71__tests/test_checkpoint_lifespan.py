"""Verify the running database server maintains admitted startup hashes."""

from threading import Event
import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from .. import database_lifespan
from ..DATABASE_SERVER_beta_C71__shared import create_app, open_database
from .DATABASE_SERVER_beta_C71__tests__shared import PIN
from .test_startup_checkpoint import _baseline, _delta, _path


class CheckpointLifespanTest(unittest.TestCase):
    def test_folds_an_addressed_update_while_server_runs(self):
        applied = Event()
        fold = database_lifespan.fold_checkpoint

        def observe(connection):
            fold(connection)
            applied.set()

        data = _baseline()
        snapshot = data["snapshot"]
        current = snapshot["atoms"][0]
        path = _path(current)
        updated = "d" * 64
        with open_database() as connection, patch.object(database_lifespan, "fold_checkpoint", observe):
            app = create_app(connection, "instance", PIN)
            with TestClient(app) as client:
                response = client.put("/generation", json=data)
                self.assertEqual(200, response.status_code, response.text)
                generation = response.json()["result"]["generation"]
                paths = [[current["relative_path"], current["filename"]]]
                delta = _delta(generation, snapshot, paths, [current], {path: updated})
                response = client.put("/generation/native-delta", json=delta)
                self.assertEqual(200, response.status_code, response.text)
                self.assertTrue(applied.wait(5), "Running server did not fold the admitted hash")
                self.assertTrue(client.get("/health").json()["result"]["ready"])
                with connection.cursor() as reader:
                    self.assertFalse(database_lifespan.checkpoint_changes_pending(reader))
                    digest = reader.execute("SELECT digest FROM ops_generation_carrier_digests WHERE path = ?",
                                            [path]).fetchone()
                    self.assertEqual((updated,), digest)
