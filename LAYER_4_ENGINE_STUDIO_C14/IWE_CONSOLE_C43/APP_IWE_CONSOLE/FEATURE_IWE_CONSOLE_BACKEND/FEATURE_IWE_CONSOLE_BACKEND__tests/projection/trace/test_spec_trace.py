from pathlib import Path
from contextlib import redirect_stderr
from io import StringIO
import subprocess
from tempfile import TemporaryDirectory
import unittest

import duckdb

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
    is_trace_path,
    native_trace_rows,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    PILOT,
    SpecTraceStore,
    remove_native_traces,
    replace_native_traces,
)


from .spec_trace_misc_cases import SpecTraceMiscCases


class SpecTraceTests(SpecTraceMiscCases, unittest.TestCase):
    def test_trace_projection_from_relocated_workbench(self):
        checkout = Path(__file__).resolve().parents[7]
        self.assertEqual(Path(__file__).resolve().parents[4], checkout / PILOT)
        directory = self.enterContext(TemporaryDirectory())
        root = Path(directory)
        module = root / PILOT / "example.py"
        module.parent.mkdir(parents=True)
        module.write_text("pass\n")
        module.with_name("example.py.spec_trace.md").write_text(
            "## Implements\n\n- AN-S-501@1\n"
        )
        connection = duckdb.connect(":memory:")
        self.addCleanup(connection.close)
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        self.assertEqual(
            connection.execute(
                "SELECT atom_id, version FROM implementation_rmedo"
            ).fetchall(),
            [("AN-S-501", 1)],
        )

    def _native_trace_fixture(self, root):
        package = root / "package"
        package.mkdir()
        module = package / "unit.py"
        module.write_text("pass")
        yaml_path = package / "package__spec_bind.yaml"
        yaml_path.write_text(
            "implements: [AN-S-3014@3]\napplies: [AN-S-9@2]\n"
        )
        (package / "package.p.spec_trace.md").write_text(
            "## Applies\n- AN-S-9@1\n"
        )
        (package / "unit.py.spec_trace.md").write_text(
            "## Implements\n- AN-S-123@4\n"
        )
        root_sidecar = root / (root.name + "__spec_bind.yaml")
        root_sidecar.write_text("implements: [AN-S-1@1]\n")
        nodes = [
            ("package:local:.", "package", "typescript", ".", None, None),
            (
                "package:local:package",
                "package",
                "python",
                "package",
                None,
                None,
            ),
            (
                "module:package/unit.py",
                "module",
                "python",
                "package/unit.py",
                "parsed",
                None,
            ),
            ("external", "package", "python", None, None, None),
            ("outside", "package", "python", "../outside", None, None),
        ]
        return nodes, yaml_path, root_sidecar

    def _assert_native_trace_rows(self, rows, root_sidecar):
        self.assertEqual(
            set(rows),
            {
                (".", root_sidecar.name, "implements", "AN-S-1", 1),
                (
                    "package",
                    "package/package__spec_bind.yaml",
                    "implements",
                    "AN-S-3014",
                    3,
                ),
                (
                    "package",
                    "package/package__spec_bind.yaml",
                    "applies",
                    "AN-S-9",
                    2,
                ),
                (
                    "package/unit.py",
                    "package/unit.py.spec_trace.md",
                    "implements",
                    "AN-S-123",
                    4,
                ),
            },
        )

    def test_native_rows_use_inventoried_owners_and_publish(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        nodes, yaml_path, root_sidecar = self._native_trace_fixture(root)
        rows = native_trace_rows(root, nodes)
        self._assert_native_trace_rows(rows, root_sidecar)
        connection = self.enterContext(duckdb.connect(":memory:"))
        replace_native_traces(connection, rows)
        self.assertEqual(
            set(
                connection.execute(
                    "SELECT * FROM implementation_rmedo"
                ).fetchall()
            ),
            set(rows),
        )
        replace_native_traces(connection, [])
        self.assertEqual(
            connection.execute(
                "SELECT * FROM implementation_rmedo"
            ).fetchall(),
            [],
        )
        remove_native_traces(connection)
        remove_native_traces(connection)
        self.assertTrue(is_trace_path("package/package__spec_bind.yaml"))
        self.assertTrue(is_trace_path("package/unit.py.spec_trace.md"))
        self.assertFalse(is_trace_path("package/unit.py"))
        yaml_path.unlink()
        self.assertIn(
            (
                "package",
                "package/package.p.spec_trace.md",
                "applies",
                "AN-S-9",
                1,
            ),
            native_trace_rows(root, nodes),
        )

    def _assert_invalid_package_traces(
        self, canonical, store, connection, query
    ):
        for invalid in (
            "implements: [CA-R-123@1]",
            "implements: [AN-S-123@0]",
            "implements: [AN-S-123@2147483648]",
            "implements: [AN-S-123@1, invalid]",
            "implements: AN-S-123@1",
            "implements: []\nimplements: []",
            "unknown: []",
            "[]",
            "implements: &pins [AN-S-123@1]\napplies: *pins",
        ):
            canonical.write_text(invalid)
            stderr = StringIO()
            with redirect_stderr(stderr):
                store.refresh([canonical])
            self.assertIn("Invalid spec trace", stderr.getvalue())
            self.assertEqual(connection.execute(query).fetchall(), [])

    def test_package_yaml_precedence_validation_and_refresh(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / "full_package_C43"
        package.mkdir(parents=True)
        canonical = package / "full_package_C43__spec_bind.yaml"
        legacy = package / "full_package_C43.p.spec_trace.md"
        legacy.write_text("## Applies\n- AN-S-9@1\n")
        connection = self.enterContext(duckdb.connect(":memory:"))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        query = "SELECT entry_kind, atom_id, version FROM implementation_rmedo ORDER BY entry_kind"
        self.assertEqual(
            connection.execute(query).fetchall(), [("applies", "AN-S-9", 1)]
        )

        canonical.write_text(
            "implements:\n  - AN-S-123@5\napplies:\n  - AN-S-9@2\n"
        )
        store.refresh([canonical])
        self.assertEqual(
            connection.execute(query).fetchall(),
            [("applies", "AN-S-9", 2), ("implements", "AN-S-123", 5)],
        )
        self._assert_invalid_package_traces(
            canonical, store, connection, query
        )
        canonical.unlink()
        store.refresh([canonical])
        self.assertEqual(
            connection.execute(query).fetchall(), [("applies", "AN-S-9", 1)]
        )
        legacy.unlink()
        store.refresh([legacy])
        self.assertEqual(connection.execute(query).fetchall(), [])

    def _assert_trace_update(self, package, store, conn, rel, module):
        (package / "unit.py.spec_trace.md").write_text(
            "## Implements\n- AN-S-123@5\n"
        )
        store.refresh([package / "unit.py.spec_trace.md"])
        assert conn.execute(
            "SELECT version FROM implementation_rmedo WHERE owner_path = ?",
            [rel(module)],
        ).fetchall() == [(5,)]
        (package / "unit.py.spec_trace.md").unlink()
        store.refresh([package / "unit.py.spec_trace.md"])
        assert (
            conn.execute(
                "SELECT * FROM implementation_rmedo WHERE owner_path = ?",
                [rel(module)],
            ).fetchall()
            == []
        )
        assert conn.execute(
            "SELECT kind FROM implementation_objects WHERE path = ?",
            [rel(module)],
        ).fetchone() == ("module",)

    def _assert_trace_objects(self, conn, rel, excluded, module, package):
        assert conn.execute(
            "SELECT atom_id, version FROM implementation_rmedo ORDER BY atom_id"
        ).fetchall() == [("AN-S-123", 4), ("AN-S-8", 3), ("AN-S-9", 2)]
        assert (
            conn.execute(
                "SELECT path FROM implementation_objects WHERE path = ?",
                [rel(excluded)],
            ).fetchall()
            == []
        )
        assert conn.execute(
            "SELECT container_path FROM implementation_objects WHERE path = ?",
            [rel(module)],
        ).fetchone() == (rel(package),)
        assert conn.execute(
            "SELECT kind, container_path FROM implementation_objects WHERE path = '.'"
        ).fetchone() == ("package", None)

    def test_incremental_trace_and_directory_changes(self):
        tmp_path = Path(self.enterContext(TemporaryDirectory()))
        pilot = tmp_path / PILOT
        package = pilot / "FEATURE_IWE_CONSOLE_BACKEND" / "sub"
        package.mkdir(parents=True)
        module = package / "unit.py"
        module.write_text("pass")
        (package / "unit.py.spec_trace.md").write_text(
            "## Implements\n- AN-S-123@4\n- AN-S-9@2\n"
        )
        (package / "sub.p.spec_trace.md").write_text(
            "## Applies\n- AN-S-8@3\n"
        )
        excluded = pilot / "FEATURE_IWE_CONSOLE_CODEX"
        excluded.mkdir()
        (excluded / "ignored.py").write_text("pass")
        (tmp_path / (tmp_path.name + ".p.spec_trace.md")).write_text(
            "## Applies\n- AN-S-999@1\n"
        )
        conn = self.enterContext(duckdb.connect(":memory:"))
        store = SpecTraceStore(conn, tmp_path)
        store.initialize()
        store.refresh()

        def rel(p):
            return p.relative_to(tmp_path).as_posix()

        self._assert_trace_objects(conn, rel, excluded, module, package)
        self._assert_trace_update(package, store, conn, rel, module)

        renamed = package.with_name("moved")
        package.rename(renamed)
        store.refresh([package, renamed])
        assert (
            conn.execute(
                "SELECT path FROM implementation_objects WHERE starts_with(path, ?)",
                [rel(package)],
            ).fetchall()
            == []
        )
        assert conn.execute(
            "SELECT kind FROM implementation_objects WHERE path = ?",
            [rel(renamed / "unit.py")],
        ).fetchone() == ("module",)
        assert (
            conn.execute("SELECT * FROM implementation_rmedo").fetchall() == []
        )
