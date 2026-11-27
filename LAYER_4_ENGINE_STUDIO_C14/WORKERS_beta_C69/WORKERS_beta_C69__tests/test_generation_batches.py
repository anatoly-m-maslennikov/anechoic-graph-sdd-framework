from hashlib import sha256
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ..generation_batches import _capture_archive
from ..managed_request import _ArchiveCapture

from .WORKERS_beta_C69__tests__shared import generation_fixture


WORKER = [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared"]


class GenerationBatchTests(unittest.TestCase):
    def test_archive_batch_merges_deferred_rows_and_hashes(self):
        current = {"atoms": [{"id": "archive"}], "relations": [], "ingestion_issues": [{"code": "a"}]}
        seed = {"snapshot": {"atoms": [{"id": "deferred"}], "relations": [{"id": "edge"}],
                             "ingestion_issues": [{"code": "b"}]}, "carrier_hashes": {"old": "1"}}
        archive = _ArchiveCapture.model_validate({"roots": [], "endpoints": {}, "seed": seed})
        with tempfile.TemporaryDirectory() as directory:
            with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.prepare_generation_snapshot",
                       return_value=(None, lambda _endpoints: (current, {"new": "2"}))):
                result = _capture_archive({}, archive, True, str(Path(directory).resolve()))
            frames = [json.loads(line) for line in (Path(directory) / "generation-batches.jsonl").read_bytes().splitlines()]
        restored = frames.pop(0)
        for section, field, rows in frames:
            if section == "carrier_hashes":
                restored[section].update(rows)
            else:
                restored[section][field].extend(rows)
        self.assertEqual(current, restored["snapshot"])
        self.assertEqual({"old": "1", "new": "2"}, restored["carrier_hashes"])
        self.assertEqual(2, len(restored["snapshot"]["atoms"]))
        self.assertEqual(2, len(restored["snapshot"]["ingestion_issues"]))
        canonical = json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(sha256(canonical).hexdigest(), result["snapshot_sha256"])

    def test_managed_full_batch_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            plain_output = output.parent / "plain"
            plain_output.mkdir()
            def run(destination, batch):
                request = {"binding": binding, "reuse": None, "batch_full": batch}
                result = subprocess.run([*WORKER, "--generation-dir", str(destination)],
                                        input=json.dumps(request), text=True, capture_output=True, timeout=120)
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            plain = run(plain_output, False)
            batched = run(output, True)
            raw = (output / "generation-batches.jsonl").read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            self.assertEqual({"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}, batched.pop("batch_artifact"))
            lines = raw.splitlines(keepends=True)
            self.assertTrue(all(len(line) <= 10 * 1024 * 1024 for line in lines))
            frames = [json.loads(line) for line in lines]
            restored = frames.pop(0)
            for section, field, rows in frames:
                if section == "carrier_hashes":
                    self.assertEqual("", field)
                    restored[section].update(rows)
                else:
                    restored[section][field].extend(rows)
            for key in ("snapshot", "graph", "carrier_hashes"):
                self.assertEqual(plain.pop(key), restored[key])
            self.assertEqual(plain, batched)
