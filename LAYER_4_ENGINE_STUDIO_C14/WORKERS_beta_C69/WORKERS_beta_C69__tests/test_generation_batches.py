from hashlib import sha256
import json
import subprocess
import sys
import tempfile
import unittest

from .WORKERS_beta_C69__tests__shared import generation_fixture


WORKER = [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared"]


class GenerationBatchTests(unittest.TestCase):
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
