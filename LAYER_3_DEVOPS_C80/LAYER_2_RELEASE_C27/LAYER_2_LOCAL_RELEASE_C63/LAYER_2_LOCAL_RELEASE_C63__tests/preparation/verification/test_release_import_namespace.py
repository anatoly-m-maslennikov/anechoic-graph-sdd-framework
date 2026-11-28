"""Keep Local Release imports within their package namespace."""

import subprocess
import sys
import unittest


class ReleaseImportNamespaceTests(unittest.TestCase):
    def test_entry_import_does_not_expose_package_directory_or_short_modules(
        self,
    ):
        code = """
import sys
before = list(sys.path)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release
assert sys.path == before
assert not any(name == "local_release" or name.startswith("local_release_")
               or name.startswith("release_") for name in sys.modules)
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", code], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
