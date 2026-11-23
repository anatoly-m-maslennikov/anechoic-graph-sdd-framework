"""Exercise the missing and invalid Saved SQL link fallback through the Backend socket."""

import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from .test_api import _client, _ready
from .WORKBENCH_BACKEND_beta_C70__tests__shared import (
    start_backend,
    stop_backend,
    write_project,
)


class SavedSqlLinksTests(unittest.TestCase):
    def test_invalid_or_missing_url_keeps_saved_id(self):
        for options in ((), ("--workbench-public-url=https://user@configured.test/custom",)):
            with self.subTest(options=options):
                self.assert_id_without_public_link(options)

    def assert_id_without_public_link(self, options):
        with TemporaryDirectory(prefix="ane-beta-url-", dir="/tmp") as directory:
            root = Path(directory).resolve()
            manifest = write_project(root)
            control = manifest.parent
            manifest = manifest.rename(root / manifest.name)
            digest = sha256(manifest.read_bytes()).hexdigest()
            socket = root / "api.sock"
            process = start_backend(root, control, manifest, digest, *options)
            try:
                with _client(socket) as api:
                    _ready(api, process, socket)
                    result = api.post("/tools", json={
                        "name": "view_save", "arguments": {"sql": "SELECT 1"}, "instance_id": "instance",
                        "session_id": None, "public_base_url": None, "asserted_project_root": None,
                    }).json()
                    value = result["result"]["value"]
                    self.assertTrue(value["saved_query_id"])
                    self.assertIsNone(value["saved_query_url"])
                    self.assertEqual("workbench_url_unknown", value["saved_query_url_reason"])
            finally:
                stop_backend(process)
            self.assertEqual(0, process.returncode)
