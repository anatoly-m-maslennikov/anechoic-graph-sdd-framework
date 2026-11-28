"""Check native claim lint through its command line."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROGRAMMATIC = Path(__file__).resolve().parents[3]


class _NativeModelLintCli:
    def test_cli_loads_native_parser_without_project_pythonpath(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claim = root / "claim.md"
            addresses = root / "addresses.json"
            relations = root / "relations.json"
            claim.write_text(
                "## Claim\n### Formal Claim\n```python\n"
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF', "
                "base_path='Atom')\n```\n"
            )
            addresses.write_text(json.dumps(["Atom"]))
            relations.write_text(json.dumps(["IS_PROPERTY_OF"]))
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(
                        PROGRAMMATIC
                        / "FEATURE_FORMAL_MODEL_ENGINE"
                        / "lint_python_model_claim__pub.py"
                    ),
                    str(claim),
                    "--addresses",
                    str(addresses),
                    "--relations",
                    str(relations),
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_accepts_model_catalog_with_explicit_python_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claim, addresses, relations = (
                root / name
                for name in ("claim.py", "addresses.json", "relations.json")
            )
            claim.write_text(
                "from anechoic.formal_claims import declare_entity\n"
                "from anechoic.model import Requirement\n"
                "class R(Requirement):\n    pass\n"
                "declare_entity(entity_class=R, entity_name='R')\n"
            )
            role = "Atom/(.Header.Context.Role:=Requirement)"
            addresses.write_text(
                json.dumps(
                    {
                        "addresses": [role],
                        "python_classes": {"Requirement": [role]},
                    }
                )
            )
            relations.write_text("[]")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(
                        PROGRAMMATIC
                        / "FEATURE_FORMAL_MODEL_ENGINE"
                        / "lint_python_model_claim__pub.py"
                    ),
                    str(claim),
                    "--addresses",
                    str(addresses),
                    "--relations",
                    str(relations),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
