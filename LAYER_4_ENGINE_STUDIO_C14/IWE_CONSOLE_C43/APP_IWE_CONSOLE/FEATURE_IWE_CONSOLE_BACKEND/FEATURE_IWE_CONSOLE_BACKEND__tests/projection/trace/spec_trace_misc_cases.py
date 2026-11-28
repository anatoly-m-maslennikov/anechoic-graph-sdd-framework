"""Additional source trace validation cases."""

import subprocess
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import PILOT, SpecTraceStore

from .....FEATURE_IMPORT_GRAPH_C61.import_graph__shared import native_trace_rows


class SpecTraceMiscCases:
    def test_native_rejects_invalid_and_symlinked_bindings(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        package = root / "package"
        package.mkdir()
        sidecar = package / "package__spec_bind.yaml"
        sidecar.write_text("implements: [AN-S-1@1, invalid]")
        nodes = [
            (
                "package:local:package",
                "package",
                "python",
                "package",
                None,
                None,
            )
        ]
        with redirect_stderr(StringIO()):
            self.assertEqual(native_trace_rows(root, nodes), [])
        sidecar.unlink()
        outside = root / "outside.yaml"
        outside.write_text("implements: [AN-S-1@1]")
        sidecar.symlink_to(outside)
        self.assertEqual(native_trace_rows(root, nodes), [])

    def test_native_pins_preserve_exact_versions(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / "example"
        package.mkdir(parents=True)
        (package / "unit.py").write_text("pass")
        sidecar = package / "unit.py.spec_trace.md"
        sidecar.write_text(
            "## Implements\n- AN-S-123@4\n- AN-S-125@12\n- AN-P-9@2\n"
        )
        connection = self.enterContext(duckdb.connect(":memory:"))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        pins = (
            "SELECT atom_id, version FROM implementation_rmedo ORDER BY "
            "atom_id"
        )
        self.assertEqual(
            connection.execute(pins).fetchall(),
            [("AN-P-9", 2), ("AN-S-123", 4), ("AN-S-125", 12)],
        )

        for invalid in ("AN-T-1@1", "AN-S-1", "AN-S-1@1-draft", "AN-S-1@0"):
            sidecar.write_text(f"## Implements\n- AN-S-123@4\n- {invalid}\n")
            with redirect_stderr(StringIO()):
                store.refresh([sidecar])
            self.assertEqual(connection.execute(pins).fetchall(), [])

    def test_sidecar_edits_replace_only_the_owner_pins(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / "example"
        package.mkdir(parents=True)
        (package / "unit.py").write_text("pass")
        module_trace = package / "unit.py.spec_trace.md"
        module_trace.write_text("## Implements\n- AN-S-123@1\n")
        package_trace = package / "example.p.spec_trace.md"
        package_trace.write_text("## Applies\n- AN-S-9@1\n")
        connection = self.enterContext(duckdb.connect(":memory:"))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        pins = (
            "SELECT atom_id, version FROM implementation_rmedo ORDER BY "
            "atom_id"
        )

        module_trace.write_text("## Implements\n- AN-S-123@2\n")
        package_trace.write_text("## Applies\n- AN-S-9@2\n")
        store.refresh([package_trace])
        self.assertEqual(
            connection.execute(pins).fetchall(),
            [("AN-S-123", 1), ("AN-S-9", 2)],
        )

        package_trace.write_text("## Applies\n- AN-S-9@3\n- invalid\n")
        stderr = StringIO()
        with redirect_stderr(stderr):
            store.refresh([package_trace])
        self.assertIn(f"{package_trace}:3:", stderr.getvalue())
        self.assertEqual(
            connection.execute(pins).fetchall(), [("AN-S-123", 1)]
        )
