"""Verify the import ownership linter through its CLI."""

from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[6]
MODULE = "LAYER_4_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_ownership"


def _lint(files):
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for relative, code in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code, encoding="utf-8")
        return subprocess.run([sys.executable, "-B", "-m", MODULE, str(root)], cwd=ROOT,
                              capture_output=True, text=True, timeout=30, check=False)


class ImportOwnershipTest(unittest.TestCase):
    def test_named_python_forwarding_resolves_to_original_owner(self):
        result = _lint({
            "owner/process.py": "class Original: pass\n",
            "owner/owner__shared.py": "from .process import Original\n",
            "bridge/private.py": "from owner.owner__shared import Original as Forwarded\n",
            "bridge/bridge__shared.py": "from .private import Forwarded as Alias\n",
            "caller/bad.py": "from bridge.bridge__shared import Alias\n",
            "caller/good.py": "from owner.owner__shared import Original\n",
        })
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("caller/bad.py:1:1: Alias passes through", result.stderr)
        self.assertIn("Import Original from the defining Package's __shared entry (owner)", result.stderr)
        self.assertNotIn("caller/good.py:", result.stderr)

    def test_a_wrapper_or_rebound_name_belongs_to_its_own_package(self):
        result = _lint({
            "owner/owner__shared.py": "class Original: pass\n",
            "bridge/bridge__shared.py": "from owner.owner__shared import Original as Alias\n"
                                        "def Alias():\n    return 1\n"
                                        "def wrap():\n    return Alias()\n",
            "caller/good.py": "from bridge.bridge__shared import Alias, wrap\n",
        })
        self.assertEqual(0, result.returncode, result.stderr)

    def test_web_forwarding_uses_the_exported_and_original_names(self):
        frontend = ROOT / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
        if shutil.which("node") is None or not all((frontend / "node_modules" / name / "package.json").is_file()
                                                  for name in ("svelte", "typescript")):
            self.skipTest("Framework-local web parsers are unavailable")
        result = _lint({
            "owner/private.ts": "export type Original = number;\n",
            "owner/owner__shared.ts": "export type { Original } from './private';\n",
            "bridge/bridge__shared.ts": "import type { Original as Local } from '../owner/owner__shared';\n"
                                        "export type { Local as Alias };\n",
            "caller/view.svelte": '<script lang="ts">import type { Alias } from "../bridge/bridge__shared";</script>',
        })
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("caller/view.svelte:1:", result.stderr)
        self.assertIn("Import Original from the defining Package's __shared entry (owner)", result.stderr)
