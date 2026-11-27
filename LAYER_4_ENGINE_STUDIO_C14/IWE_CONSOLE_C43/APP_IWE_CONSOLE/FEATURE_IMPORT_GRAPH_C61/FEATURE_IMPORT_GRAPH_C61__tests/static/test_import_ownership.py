"""Verify the import ownership linter through its CLI."""

from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[6]
MODULE = (
    "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_ownership"
)


def _lint(files):
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for relative, code in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code, encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", "-m", MODULE, str(root)],
            cwd=ROOT / "LAYER_4_ENGINE_STUDIO_C14",
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )


class ImportOwnershipTest(unittest.TestCase):
    def test_named_python_forwarding_resolves_to_original_owner(self):
        result = _lint(
            {
                "owner/process.py": "class Original: pass\n",
                "owner/owner__shared.py": "from .process import Original\n",
                "bridge/private.py": (
                    "from owner.owner__shared import Original as Forwarded\n"
                ),
                "bridge/bridge__shared.py": (
                    "from .private import Forwarded as Alias\n"
                ),
                "caller/bad.py": "from bridge.bridge__shared import Alias\n",
                "caller/good.py": "from owner.owner__shared import Original\n",
                "caller/caller__shared.py": "pass\n",
            }
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("caller/bad.py:1:1: Alias passes through", result.stderr)
        self.assertIn(
            "Import Original from the defining Package's entry (owner)",
            result.stderr,
        )
        self.assertNotIn("caller/good.py:", result.stderr)

    def test_a_wrapper_or_rebound_name_belongs_to_its_own_package(self):
        result = _lint(
            {
                "owner/owner__shared.py": "class Original: pass\n",
                "bridge/bridge__shared.py": (
                    "from owner.owner__shared import Original as Alias\ndef "
                    "Alias():\n    return 1\ndef wrap():\n    return Alia"
                    "s()\n"
                ),
                "caller/good.py": (
                    "from bridge.bridge__shared import Alias, wrap\n"
                ),
                "caller/caller__public.py": "pass\n",
            }
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_web_forwarding_uses_the_exported_and_original_names(self):
        frontend = ROOT / (
            "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEA"
            "TURE_IWE_CONSOLE_FRONTEND"
        )
        if shutil.which("node") is None or not all(
            (frontend / "node_modules" / name / "package.json").is_file()
            for name in ("svelte", "typescript")
        ):
            self.skipTest("Framework-local web parsers are unavailable")
        result = _lint(
            {
                "owner/private.ts": "export type Original = number;\n",
                "owner/owner__shared.ts": (
                    "export type { Original } from './private';\n"
                ),
                "bridge/bridge__shared.ts": (
                    "import type { Original as Local } from "
                    "'../owner/owner__shared';\nexport type { Local as "
                    "Alias };\n"
                ),
                "caller/view.svelte": (
                    '<script lang="ts">import type { Alias } from '
                    '"../bridge/bridge__shared";</script>'
                ),
                "caller/caller__shared.py": "pass\n",
            }
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("caller/view.svelte:1:", result.stderr)
        self.assertIn(
            "Import Original from the defining Package's entry (owner)",
            result.stderr,
        )


class PackageEntryTest(unittest.TestCase):
    def test_static_gate_checks_direct_code_and_grouping_folders(self):
        result = _lint(
            {
                "missing/main.py": "pass\n",
                "missing/child/child__shared.py": "pass\n",
                "many/a__shared.py": "pass\n",
                "many/b__public.py": "pass\n",
                "group/child/child__shared.py": "",
                "marked/_bypass__shared.py": "",
                "marked/child/child__shared.py": "",
                "tests__tests/test_main.py": "pass\n",
                "test_only/fixtures__tests/unit/test_main.py": "pass\n",
                "alias/alias__pub.py": "pass\n",
                "public/public__public.py": "pass\n",
                "shared/shared__shared.py": "pass\n",
                "declarations/types.d.ts": "export type T = string;\n",
                "declarations/types.d.cts": "export type T = string;\n",
                "declarations/types.d.mts": "export type T = string;\n",
                "assets/style.css": "body {}\n",
            }
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self._assert_package_entries(result.stderr)

    def _assert_package_entries(self, diagnostics):
        for folder, count in (
            ("missing", 0),
            ("many", 2),
            ("alias", 0),
            ("group", 0),
        ):
            self.assertIn(
                (
                    "Expected one __shared or __public entry in "
                    f"{folder}"
                    ", found "
                    f"{count}"
                ),
                diagnostics,
            )
        for folder in (
            "missing/child",
            "marked",
            "marked/child",
            "public",
            "shared",
            "tests__tests",
            "test_only",
            "test_only/fixtures__tests",
            "test_only/fixtures__tests/unit",
            "declarations",
            "assets",
        ):
            self.assertNotIn(f"entry in {folder},", diagnostics)

    def test_static_gate_accepts_a_single_direct_entry(self):
        result = _lint(
            {
                "example/main.py": "pass\n",
                "example/example__public.py": "pass\n",
            }
        )
        self.assertEqual(0, result.returncode, result.stderr)
