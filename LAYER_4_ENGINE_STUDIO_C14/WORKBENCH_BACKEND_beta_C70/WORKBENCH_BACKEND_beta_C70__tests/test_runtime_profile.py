"""Check profile precedence and peer arguments."""

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest import TestCase
from unittest.mock import patch

from WORKBENCH_BACKEND_beta_C70.runtime import (
    DATABASE,
    ORCHESTRATOR,
    database_path,
    open_project_peers,
)
from WORKBENCH_BACKEND_beta_C70.runtime_profile import resolve_runtime_profile


class RuntimeProfileTests(TestCase):
    def test_profiles_and_legacy_defaults(self):
        profiles = {
            "dev-local": ("memory", "files", "skip"),
            "dev-preprod": ("disk", "duckdb", "load"),
            "test": ("memory", "files", "load"),
            "prod": ("disk", "duckdb", "load"),
        }
        for name, expected in profiles.items():
            with self.subTest(name=name):
                self.assertEqual(expected, resolve_runtime_profile("disk", "files", {"ANECHOIC_RUNTIME_PROFILE": name}))
        self.assertEqual(("disk", "files", "load"), resolve_runtime_profile("disk", "files", {}))

    def test_overrides_and_invalid_values(self):
        env = {"ANECHOIC_RUNTIME_PROFILE": "test", "ANECHOIC_JOURNAL_STORAGE": "duckdb"}
        self.assertEqual(("memory", "duckdb", "load"), resolve_runtime_profile("disk", "files", env))
        self.assertEqual(("disk", "files", "skip"), resolve_runtime_profile(
            "disk", "files", {"ANECHOIC_RUNTIME_PROFILE": "dev-local", "ANECHOIC_WORKBENCH_STORAGE": "disk"}))
        for env in ({"ANECHOIC_RUNTIME_PROFILE": "unknown"}, {"ANECHOIC_ARCHIVES": "bad"},
                    {"ANECHOIC_RUNTIME_PROFILE": "prod", "ANECHOIC_ARCHIVES": "skip"},
                    {"ANECHOIC_JOURNAL_STORAGE": "bad"}, {"ANECHOIC_WORKBENCH_STORAGE": "bad"}):
            with self.subTest(env=env), self.assertRaises(ValueError):
                resolve_runtime_profile("disk", "files", env)

    def test_disk_projection_paths_are_isolated(self):
        with TemporaryDirectory() as tmp:
            root = str(Path(tmp).resolve())
            digest = "a" * 64
            production = database_path(root, "disk", digest, "id")
            local_skip = database_path(root, "disk", digest, "id", local_archives="skip")
            local_load = database_path(root, "disk", digest, "id", local_archives="load")
            self.assertEqual(3, len({production, local_skip, local_load}))
            self.assertTrue(local_skip.name.endswith("-dev-local-skip.duckdb"))
            self.assertTrue(local_load.name.endswith("-dev-local-load.duckdb"))
            self.assertTrue(production.name.endswith(digest + ".duckdb"))

    def test_disk_profile_passes_isolated_path_to_kernel(self):
        for mode in ("skip", "load"):
            calls = []

            @contextmanager
            def peer(module, path, instance_id, stop, *args, captured=calls):
                captured.append((module, args))
                yield object()

            env = {"ANECHOIC_RUNTIME_PROFILE": "dev-local", "ANECHOIC_WORKBENCH_STORAGE": "disk",
                   "ANECHOIC_ARCHIVES": mode}
            with self.subTest(mode=mode), TemporaryDirectory() as tmp, patch.dict("os.environ", env, clear=True):
                binding = {"root": str(Path(tmp).resolve()), "control_root": "_anechoic_example", "manifest_sha256": "a" * 64}
                with (patch("WORKBENCH_BACKEND_beta_C70.runtime._peer", peer),
                      open_project_peers(Path(tmp), "id", binding, Event())):
                    pass
                database = dict(calls)[DATABASE]
                actual = database[database.index("--database-path") + 1]
                self.assertTrue(actual.endswith(f"-dev-local-{mode}.duckdb"))
                self.assertEqual(mode == "skip", "--skip-archives" in dict(calls)[ORCHESTRATOR])

    def test_peer_arguments_use_profile_not_manifest(self):
        calls = []

        @contextmanager
        def peer(module, path, instance_id, stop, *args):
            calls.append((module, args))
            yield object()

        with TemporaryDirectory() as tmp, patch.dict("os.environ", {"ANECHOIC_RUNTIME_PROFILE": "dev-local"}, clear=True):
            binding = {"root": str(Path(tmp).resolve()), "control_root": "_anechoic_example", "manifest_sha256": "a" * 64}
            with (patch("WORKBENCH_BACKEND_beta_C70.runtime._peer", peer),
                  open_project_peers(Path(tmp), "id", binding, Event(), storage="disk", journal_storage="duckdb")):
                pass
        database = dict(calls)[DATABASE]
        orchestrator = dict(calls)[ORCHESTRATOR]
        self.assertEqual("files", database[database.index("--journal-storage") + 1])
        self.assertNotIn("--database-path", database)
        self.assertIn("--skip-archives", orchestrator)
        self.assertNotIn("--skip-archives", database)
