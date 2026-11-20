import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError

from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure


HOST = "LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.host"


class HostTest(unittest.TestCase):
    def test_publication_and_immutable_reads(self):
        data = {"model_sha256": "model", "project": {"ref": "project", "sha256": "hash"},
                "components": {"C14": {"parent": "C00", "ref": "AN-S-1", "sha256": "hash",
                                       "fields": {"name": "Studio", "lens_whitelist": ["SPEC"]},
                                       "source_path": "components/studio.md"}}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "active.json"
            with subprocess.Popen([sys.executable, "-m", HOST, str(path), "model"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as host:
                def send(content):
                    path.with_suffix(".pending").write_bytes(content)
                    host.stdin.write(b"publish\n")
                    host.stdin.flush()
                    return host.stdout.readline().strip()

                self.assertEqual(send(json.dumps(data).encode()), b"ready")
                first = read_structure(path)
                component = first.component("C14")
                self.assertEqual((component.name, component.parent, component.source_path),
                                 ("Studio", "C00", "components/studio.md"))
                self.assertEqual(component.lens_whitelist, ("SPEC",))
                with self.assertRaises(TypeError):
                    component.fields["name"] = "changed"
                with self.assertRaises(FrozenInstanceError):
                    component.parent = None
                self.assertEqual(send(b"{invalid"), b"invalid")
                data["model_sha256"] = "wrong"
                self.assertEqual(send(json.dumps(data).encode()), b"invalid")
                self.assertEqual(read_structure(path).component("C14").name, "Studio")
                data["model_sha256"] = "model"
                data["components"]["C14"]["fields"]["name"] = "Changed"
                self.assertEqual(send(json.dumps(data).encode()), b"ready")
                self.assertEqual(first.component("C14").name, "Studio")
                self.assertEqual(read_structure(path).component("C14").name, "Changed")
                host.stdin.close()
                self.assertEqual(host.wait(timeout=5), 0)

    def test_invalid_paths_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "active.json"
            path.write_text('{"model_sha256":"x", "model_sha256":"y"}')
            with self.assertRaises(ValueError):
                read_structure(path)
            data = {"model_sha256": "x", "project": {"ref": "p", "sha256": "h"},
                    "components": {"C": {"parent": None, "ref": "r", "sha256": "h",
                                         "fields": {"name": "n"}, "source_path": "../outside"}}}
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                read_structure(path)


if __name__ == "__main__":
    unittest.main()
