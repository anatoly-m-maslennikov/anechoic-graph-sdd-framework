"""Exercise existing access findings through a captured Beta graph."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ENGINE = Path(__file__).resolve().parents[2]


class ExistingAccessFindingsTest(unittest.TestCase):
    def _findings(self, root, structure, source):
        request = {
            "root": str(root),
            "config": {"python_roots": ["."]},
            "structure": structure,
            "control_root": "_control",
        }
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                "WORKERS_beta_C69.realization_graph",
            ],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=60,
            env=os.environ | {"PYTHONPATH": str(ENGINE)},
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return [
            row
            for row in json.loads(result.stdout)["code_access_findings"]
            if row[1] == source
        ]

    def _setup_widget(self, root):
        (root / "_control/_SPEC").mkdir(parents=True)
        (root / "_control/Widget_C9").mkdir()
        (root / "Widget/lib").mkdir(parents=True)
        (root / "Widget/client").mkdir()
        (root / "Widget/lib/parse.py").write_text("def run(): return 1\n")
        (root / "Widget/lib/__init__.py").write_text(
            "from .parse import run\n"
        )
        (root / "Widget/client/run.py").write_text(
            "from Widget.lib.parse import run\n"
            "from Widget.lib.parse import *\nfrom Widget.lib import run\n"
        )
        code = {
            "imports": ["lib.parse.run"],
            "exports": {
                "lib.parse.run": {"private": ["Widget/client"]},
                "lib.run": "public",
            },
        }
        code["imports"].append("lib.run")
        structure = {
            "model_sha256": "model",
            "project": {"ref": "AN-S-1", "sha256": "hash"},
            "components": {
                "C9": {
                    "parent": "C00",
                    "ref": "AN-S-2",
                    "sha256": "hash",
                    "fields": {
                        "name": "Widget",
                        "boundaries": {"code": code},
                    },
                    "source_path": "_SPEC/spec.md",
                }
            },
            "packages": {},
        }

        return code, structure

    def test_cross_package_access_and_declared_exception(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            code, structure = self._setup_widget(root)

            def findings():
                return self._findings(root, structure, "Widget/client/run.py")

            rows = findings()
            self.assertEqual(
                [(row[4], row[5], row[6]) for row in rows],
                [
                    (
                        "from Widget.lib.parse import run",
                        "declared_bypass",
                        "exact import and export declarations",
                    ),
                    (
                        "from Widget.lib.parse import *",
                        "uncertain",
                        "wildcard import",
                    ),
                    (
                        "from Widget.lib import run",
                        "declared_bypass",
                        "exact import and export declarations",
                    ),
                ],
            )
            code["exports"]["lib.parse.run"] = {"private": []}
            self.assertEqual("denied", findings()[0][5])
            code["exports"]["lib.parse.run"] = "public"
            self.assertEqual("declared_bypass", findings()[0][5])

    def test_reversed_sibling_layer_is_denied(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "_control/_SPEC").mkdir(parents=True)
            for name in ("Low_C1", "High_C2"):
                (root / "_control" / name).mkdir()
            (root / "Low").mkdir()
            (root / "High").mkdir()
            (root / "Low/main.py").write_text("from High.api import run\n")
            (root / "High/api.py").write_text("def run(): return 1\n")

            def component(name, layer, code=None):
                fields = {"name": name, "layer": layer}
                if code is not None:
                    fields["boundaries"] = {"code": code}
                return {
                    "parent": "C00",
                    "ref": "AN-S-2",
                    "sha256": "hash",
                    "fields": fields,
                    "source_path": "_SPEC/spec.md",
                }

            structure = {
                "model_sha256": "model",
                "project": {"ref": "AN-S-1", "sha256": "hash"},
                "components": {
                    "C1": component("Low", 1),
                    "C2": component(
                        "High", 2, {"exports": {"api.run": "public"}}
                    ),
                },
                "packages": {},
            }
            rows = self._findings(root, structure, "Low/main.py")
            self.assertEqual(
                [("denied", "sibling layer order")],
                [(row[5], row[6]) for row in rows],
            )


if __name__ == "__main__":
    unittest.main()
