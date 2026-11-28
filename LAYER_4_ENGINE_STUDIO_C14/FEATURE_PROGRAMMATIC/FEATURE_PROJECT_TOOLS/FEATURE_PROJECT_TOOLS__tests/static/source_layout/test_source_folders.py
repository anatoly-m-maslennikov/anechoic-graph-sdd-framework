"""Verify the 67 Rule on the Static source inventory."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    source_inventory import source_sizes


class SourceFolderTests(unittest.TestCase):
    def test_static_rejects_only_exceeded_direct_limits(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(("git", "init", "--quiet", str(root)), check=True)
        folder = root / source_sizes.PROGRAMMATIC_ROOT / "example"
        folder.mkdir(parents=True)
        for index in range(7):
            (folder / f"tool{index}.sh").write_bytes(b"#" * 5376)
        script = b"#!/bin/sh\n"
        (folder / "run").write_bytes(script.ljust(5376, b"#"))
        (folder / "package-lock.json").write_bytes(b" " * 61440)
        for index in range(6):
            (folder / f"asset{index}.bin").write_bytes(b"x" * 5376)
        for index in range(5):
            self._child(folder / f"child{index}")
        self._child(folder / "example__tests")
        self._child(folder / ".anechoic_runtime")
        (root / ".gitignore").write_text("ignored.sh\n")
        (folder / "ignored.sh").write_bytes(b"#" * 43009)

        self.assertEqual(source_sizes.check(root), 0)

        (folder / "last.rs").write_bytes(b"x")
        (folder / "extra.bin").write_bytes(b"x")
        self._child(folder / "child5")
        self._child(folder / "another__tests")
        errors = StringIO()
        with redirect_stderr(errors):
            self.assertEqual(source_sizes.check(root), 1)
        prefix = f"{folder.relative_to(root)}: 67 Rule:"
        self.assertEqual(
            [
                f"{prefix} direct executable files total 43009 bytes "
                "(maximum 43008)",
                f"{prefix} 8 direct non-executable files (maximum 7)",
                f"{prefix} 6 ordinary direct subfolders (maximum 5)",
                f"{prefix} 2 direct test subfolders (maximum 1)",
            ],
            [
                item
                for item in errors.getvalue().splitlines()
                if prefix in item
            ],
        )

    def test_components_do_not_consume_parent_folder_slots(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(("git", "init", "--quiet", str(root)), check=True)
        parent = root / source_sizes.PROGRAMMATIC_ROOT
        parent.mkdir(parents=True)
        for index in range(4):
            self._child(parent / f"child{index}")
        self._child(parent / "ordinary_C999")
        component = parent / "declared_C24"
        self._child(component)

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS."
            "source_folders._component_folders",
            return_value={component.relative_to(root)},
        ):
            self.assertEqual(source_sizes.check(root), 0)
            self._child(parent / "another")
            (component / "tool.sh").write_bytes(b"#" * 43009)
            errors = StringIO()
            with redirect_stderr(errors):
                self.assertEqual(source_sizes.check(root), 1)
            self.assertIn(
                "6 ordinary direct subfolders (maximum 5)", errors.getvalue()
            )
            self.assertIn(
                f"{component.relative_to(root)}: 67 Rule: direct executable "
                "files total 43009 bytes",
                errors.getvalue(),
            )

    def _child(self, folder):
        folder.mkdir()
        (folder / "data.txt").write_text("content\n")
