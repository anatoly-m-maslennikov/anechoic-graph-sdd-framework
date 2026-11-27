import json
from dataclasses import FrozenInstanceError
from pathlib import Path
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import read_structure  # fmt: skip
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_CS3.\
    structure_host_CS3__shared \
    import publish_structure  # fmt: skip


class HostTest(unittest.TestCase):
    def test_publication_and_immutable_reads(self):
        data = {
            "model_sha256": "model",
            "project": {"ref": "project", "sha256": "hash"},
            "components": {
                "C14": {
                    "parent": "C00",
                    "ref": "AN-S-1",
                    "sha256": "hash",
                    "fields": {"name": "Studio", "lens_whitelist": ["SPEC"]},
                    "source_path": "components/studio.md",
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "active.json"
            publish_structure(path, "model", json.dumps(data).encode())
            first = read_structure(path)
            component = first.component("C14")
            self.assertEqual(
                (component.name, component.parent, component.source_path),
                ("Studio", "C00", "components/studio.md"),
            )
            self.assertEqual(component.lens_whitelist, ("SPEC",))
            with self.assertRaises(TypeError):
                component.fields["name"] = "changed"
            with self.assertRaises(FrozenInstanceError):
                component.parent = None
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                publish_structure(path, "model", b"{invalid")
            data["model_sha256"] = "wrong"
            with self.assertRaises(ValueError):
                publish_structure(path, "model", json.dumps(data).encode())
            self.assertEqual(before, path.read_bytes())
            data["model_sha256"] = "model"
            data["components"]["C14"]["fields"]["name"] = "Changed"
            publish_structure(path, "model", json.dumps(data).encode())
            self.assertEqual(first.component("C14").name, "Studio")
            self.assertEqual(
                read_structure(path).component("C14").name, "Changed"
            )

    def test_invalid_paths_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "active.json"
            path.write_text('{"model_sha256":"x", "model_sha256":"y"}')
            with self.assertRaises(ValueError):
                read_structure(path)
            data = {
                "model_sha256": "x",
                "project": {"ref": "p", "sha256": "h"},
                "components": {
                    "C": {
                        "parent": None,
                        "ref": "r",
                        "sha256": "h",
                        "fields": {"name": "n"},
                        "source_path": "../outside",
                    }
                },
            }
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                read_structure(path)


if __name__ == "__main__":
    unittest.main()
