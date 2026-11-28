"""Exercise filename version seed admission through both generation paths."""

import tempfile
import unittest

from starlette.testclient import TestClient

from ....DATABASE_SERVER_beta_C71__shared import create_app, open_database
from .test_archive_generation import _partial
from ..generation.test_generation_batch import _frames, _stage


class ArchiveSeedTests(unittest.TestCase):
    def test_direct_seed_validation_and_warm_cache(self):
        data, _, _ = _partial()
        with (
            open_database() as connection,
            TestClient(create_app(connection, "instance", "a" * 64)) as client,
        ):
            for seed in (
                {"invalid": 1},
                {"AN-T-1": 0},
                {"AN-T-1": True},
                {"AN-T-1": 2**63},
                [],
            ):
                response = client.put(
                    "/generation", json=data | {"archive_versions": seed}
                )
                self.assertEqual(400, response.status_code, response.text)
                self.assertEqual(
                    0,
                    connection.execute(
                        "SELECT count(*) FROM ops_generation"
                    ).fetchone()[0],
                )
            response = client.put(
                "/generation", json=data | {"archive_versions": {"AN-T-1": 7}}
            )
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                [("AN-T-1", 7)],
                connection.execute(
                    "SELECT * FROM main.ops_archive_versions"
                ).fetchall(),
            )
            response = client.put(
                "/generation", json=data | {"archive_versions": {"AN-T-1": 2}}
            )
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                [("AN-T-1", 7)],
                connection.execute(
                    "SELECT * FROM main.ops_archive_versions"
                ).fetchall(),
            )

    def test_batch_accepts_empty_seed(self):
        data, _, _ = _partial()
        with (
            tempfile.TemporaryDirectory(
                prefix="anechoic-generation-"
            ) as directory,
            open_database() as connection,
            TestClient(create_app(connection, "instance", "a" * 64)) as client,
        ):
            frames = _frames(data)
            graph = frames[0]["graph"]
            for key, value in list(graph.items()):
                if isinstance(value, list):
                    frames.append(["graph", key, value])
                    graph[key] = []
            batch = _stage(directory, frames)
            request = {
                k: v
                for k, v in data.items()
                if k not in {"snapshot", "graph", "carrier_hashes"}
            }
            response = client.put(
                "/generation",
                json=request
                | {"batch_artifact": batch, "archive_versions": {}},
            )
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual(
                [],
                connection.execute(
                    "SELECT * FROM main.ops_archive_versions"
                ).fetchall(),
            )
