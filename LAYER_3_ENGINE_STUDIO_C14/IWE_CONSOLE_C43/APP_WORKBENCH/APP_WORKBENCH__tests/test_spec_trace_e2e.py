"""Exercise spec trace projections through Workbench and the native watcher."""
import asyncio
from pathlib import Path
import sys
import tempfile
import time
import unittest

REPOSITORY = Path(__file__).resolve().parents[4]
PROGRAMMATIC = REPOSITORY / "LAYER_3_ENGINE_STUDIO_C14" / "FEATURE_PROGRAMMATIC"
APP_ROOT = PROGRAMMATIC.parent / "IWE_CONSOLE_C43" / "APP_WORKBENCH"
for location in (PROGRAMMATIC.parent / "MCP_PATCHBAY_C21" / "FEATURE_MCP", APP_ROOT.parent, APP_ROOT, APP_ROOT / "APP_WORKBENCH__tests"):
    sys.path.insert(0, str(location))

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.service import WorkbenchService  # noqa: E402
from FEATURE_TOOLS__tests.scope_declaration_test_support import write_scope_unit_declarations  # noqa: E402
from smalltest_support import built_assets, extension_directory, write_atom, write_settings  # noqa: E402
from workbench_tools import WorkbenchTools  # noqa: E402


class ConfiguredTools(WorkbenchTools):
    def _owner(self):
        if self._service is None:
            self._service = WorkbenchService(
                self.root, extension_directory=extension_directory(REPOSITORY), **built_assets(self.root),
            )
        return self._service


class SpecTraceE2E(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        control = write_settings(self.root)
        declarations = write_scope_unit_declarations(self.root, control_root=control)
        authority = Path(next(iter(declarations.values()))["authority_path"])
        write_atom(authority / "04_requirement" / "archived" / "CA-R-501@1.md",
                   "CA-R-501", status="Archived")
        self.pilot = self.root / "LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH"
        self.pilot.mkdir(parents=True)
        self.prefix = self.pilot.relative_to(self.root).as_posix()
        self.package = self.pilot / "example"
        self.package.mkdir()
        self.module = self.package / "example.py"
        self.module.write_text("pass\n")
        self.sidecar = self.package / "example.py.spec_trace.md"
        self.tools = ConfiguredTools(self.root)
        self.addCleanup(lambda: asyncio.run(self.tools.close()))
        self.sql("SELECT 1")

    def call(self, name, args):
        return asyncio.run(self.tools.call(name, args))

    def sql(self, sql):
        return self.call("query_run", {"sql": sql, "result_delivery": "inline"})["rows"]

    def test_existing_pin_is_queryable_at_startup_and_after_reread(self):
        self.sidecar.write_text("## Implements\n\n- CA-R-501@1\n")
        self.call("workbench_restart", {})
        pins = """SELECT o.kind, r.entry_kind, r.atom_id, r.version
            FROM implementation_objects o JOIN implementation_rmedo r ON o.path = r.owner_path"""
        expected = [["module", "implements", "CA-R-501", 1]]
        self.assertEqual(expected, self.sql(pins))
        self.call("workbench_reread", {})
        self.assertEqual(expected, self.sql(pins))

    def wait(self, sql, expected):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            rows = self.sql(sql)
            if rows == expected:
                return
            time.sleep(0.1)
        self.fail(f"watcher projection did not converge: {sql}\nexpected={expected!r}, got={rows!r}")

    def test_applies_pins_do_not_count_as_implementation(self):
        package = self.package.relative_to(self.root).as_posix()
        (self.package / "example__spec_bind.yaml").write_text("applies:\n  - CA-M-501@1\n")
        self.wait("SELECT owner_path, entry_kind FROM implementation_rmedo", [[package, "applies"]])
        self.assertEqual([[package, 0, 0]], self.sql(f"""
            SELECT o.path, count(r.atom_id) FILTER (WHERE r.owner_path = o.path), count(r.atom_id)
            FROM implementation_objects o
            LEFT JOIN implementation_rmedo r ON r.entry_kind = 'implements'
              AND (r.owner_path = o.path OR starts_with(r.owner_path, o.path || '/'))
            WHERE o.path = '{package}' GROUP BY o.path
        """))

    def test_watcher_and_reread(self):
        objects = f"SELECT path, kind FROM implementation_objects WHERE path LIKE '{self.prefix}/example%' ORDER BY path"
        package = self.prefix + "/example"
        module = package + "/example.py"
        pins = "SELECT owner_path, entry_kind, atom_id, version FROM implementation_rmedo ORDER BY 1, 2, 3, 4"
        tables = self.call("query_schema", {})["tables"]
        self.assertIn("implementation_objects", tables)
        self.assertIn("implementation_rmedo", tables)
        self.assertEqual([[package, "package"], [module, "module"]], self.sql(objects))
        self.assertEqual([], self.sql(pins))
        # Both direct and subtree coverage must include an uncovered object.
        coverage = f"""SELECT o.path, count(r.atom_id) FROM implementation_objects o
            LEFT JOIN implementation_rmedo r ON r.entry_kind = 'implements'
                AND (r.owner_path = o.path OR starts_with(r.owner_path, o.path || '/'))
            WHERE o.path IN ('{package}', '{module}') GROUP BY o.path ORDER BY o.path"""
        self.assertEqual([[package, 0], [module, 0]], self.sql(coverage))
        self.sidecar.write_text("## Implements\n\n- CA-R-501@1\n")
        self.wait(pins, [[module, "implements", "CA-R-501", 1]])
        self.assertEqual([], self.sql('SELECT "header.atom_id" FROM atoms WHERE "header.atom_id" = \'CA-R-501\''))
        self.sidecar.write_text("## Implements\n\n- CA-R-501@1\n- invalid\n")
        self.wait(pins, [])
        self.sidecar.write_text("## Implements\n\n- CA-R-501@2\n")
        self.wait(pins, [[module, "implements", "CA-R-501", 2]])
        renamed = self.package / "other.py.spec_trace.md"
        self.sidecar.rename(renamed)
        self.wait(pins, [])
        renamed.rename(self.sidecar)
        self.wait(pins, [[module, "implements", "CA-R-501", 2]])
        moved = self.pilot / "other.py.spec_trace.md"
        self.sidecar.rename(moved)
        self.wait(pins, [])
        moved.rename(self.sidecar)
        self.wait(pins, [[module, "implements", "CA-R-501", 2]])
        self.sidecar.unlink()
        self.wait(pins, [])
        renamed_module = self.package / "other.py"
        self.module.rename(renamed_module)
        self.wait(objects, [[package, "package"], [package + "/other.py", "module"]])
        moved_module = self.pilot / "other.py"
        renamed_module.rename(moved_module)
        self.wait(objects, [[package, "package"]])
        moved_module.unlink()
        self.wait(f"SELECT path FROM implementation_objects WHERE path = '{self.prefix}/other.py'", [])
        self.assertEqual([], self.sql(f"""SELECT old_path, new_path FROM change_log
            WHERE starts_with(old_path, '{self.prefix}/') OR starts_with(new_path, '{self.prefix}/')"""))
        before = (self.sql(objects), self.sql(pins), self.sql(coverage))
        self.assertEqual({"service": "workbench", "status": "ready"}, self.call("workbench_reread", {}))
        self.assertEqual(before, (self.sql(objects), self.sql(pins), self.sql(coverage)))


if __name__ == "__main__":
    unittest.main()
