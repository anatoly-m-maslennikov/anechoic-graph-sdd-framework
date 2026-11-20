import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HOST = "LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_pkg2.host"


class HostTest(unittest.TestCase):
    def test_admit_and_reject_changed_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            generation = Path(directory)
            package = generation / "anechoic_runtime_model"
            package.mkdir()
            contents = {"__init__.py": b"", "example.py": b"VALUE = 1\n"}
            for name, content in contents.items():
                (package / name).write_bytes(content)
            model_hash = "a" * 64
            (generation / "model.json").write_text(json.dumps({
                "model_sha256": model_hash,
                "modules": {name: hashlib.sha256(content).hexdigest() for name, content in contents.items()},
            }))
            command = [sys.executable, "-m", HOST, str(generation), model_hash]
            with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as host:
                self.assertEqual(host.stdout.readline(), b"ready\n")
                self.assertIsNone(host.poll())
                host.stdin.close()
                self.assertEqual(host.wait(timeout=5), 0)
            (package / "example.py").write_text("VALUE = 2\n")
            rejected = subprocess.run(command, input=b"", capture_output=True, timeout=5)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout, b"")


if __name__ == "__main__":
    unittest.main()
