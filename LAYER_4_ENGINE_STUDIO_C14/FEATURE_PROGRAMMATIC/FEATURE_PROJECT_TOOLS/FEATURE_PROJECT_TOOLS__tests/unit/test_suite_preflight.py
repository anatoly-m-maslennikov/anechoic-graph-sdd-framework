"""Check prerequisite diagnostics and the offline preflight command."""

import io
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import call, MagicMock, patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import suite_preflight as preflight
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import test_suite__shared as runner


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()

    def write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_frontend_uses_installed_locked_versions_and_offline_commands(self):
        frontend = self.root / preflight.FRONTEND
        manifest = {"devDependencies": {"playwright": "^1.0"}}
        self.write_json(frontend / "package.json", manifest)
        self.write_json(frontend / "package-lock.json", {"packages": {
            "": manifest, "node_modules/playwright": {"version": "1.1.0"},
            "node_modules/another-platform": {"version": "1.0.0", "optional": True},
        }})
        installed = frontend / "node_modules/playwright/package.json"
        with patch.object(preflight, "_run") as run:
            with self.assertRaises(FileNotFoundError):
                preflight._check_frontend(frontend)
            self.write_json(installed, {"version": "1.2.0"})
            with self.assertRaisesRegex(ValueError, "package-lock.json pins 1.1.0"):
                preflight._check_frontend(frontend)
            run.assert_not_called()
            self.write_json(installed, {"version": "1.1.0"})
            preflight._check_frontend(frontend)
        npm, native = [entry.args for entry in run.call_args_list]
        self.assertEqual(("npm", "ls"), npm[0][:2])
        self.assertIn("--offline", npm[0])
        self.assertIn("--ignore-scripts", npm[0])
        self.assertEqual("node", native[0][0])
        self.assertEqual(frontend, npm[1])
        self.assertEqual(frontend, native[1])

    def test_duckpgq_loads_cached_extension_in_the_pinned_engine(self):
        duckdb = MagicMock(__version__="2.0.0")
        extensions = self.root / "extensions"
        config = {"dependency-groups": {"runtime": ["duckdb==2.0.0"]}}
        connection = duckdb.connect.return_value.__enter__.return_value
        connection.execute.return_value.fetchone.return_value = (preflight.DUCKPGQ_VERSION,)
        with (patch.dict(preflight.sys.modules, {"duckdb": duckdb}),
              patch.object(preflight, "load_suite_config", return_value=config)):
            preflight._check_duckpgq(self.root, extensions)
            duckdb.__version__ = "2.0.1"
            with self.assertRaisesRegex(ValueError, "does not match the engine pin"):
                preflight._check_duckpgq(self.root, extensions)
        duckdb.connect.assert_called_once_with(":memory:", config={
            "extension_directory": str(extensions), "autoinstall_known_extensions": False,
            "autoload_known_extensions": False,
        })
        self.assertEqual(connection.execute.call_args_list, [
            call("LOAD duckpgq"), call("SET active_grammar_extensions = ['duckpgq']"),
            call("SELECT extension_version FROM duckdb_extensions() WHERE extension_name = 'duckpgq' AND loaded"),
        ])

    def test_duckpgq_rejects_a_loadable_unpinned_extension(self):
        duckdb = MagicMock(__version__="2.0.0")
        config = {"dependency-groups": {"runtime": ["duckdb==2.0.0"]}}
        connection = duckdb.connect.return_value.__enter__.return_value
        connection.execute.return_value.fetchone.return_value = ("wrong-revision",)
        with (patch.dict(preflight.sys.modules, {"duckdb": duckdb}),
              patch.object(preflight, "load_suite_config", return_value=config),
              self.assertRaisesRegex(ValueError, "Loaded DuckPGQ wrong-revision; expected")):
            preflight._check_duckpgq(self.root, self.root / "extensions")

    def test_chromium_executes_the_browser_e2e_probe_with_a_bound(self):
        probe = self.root / preflight.CHROMIUM_PROBE
        probe.parent.mkdir(parents=True)
        probe.write_text('await chromium.launch({channel: "chromium"});', encoding="utf-8")
        browsers = self.root / preflight.WORKBENCH_CACHE / "playwright-browsers"
        with patch.object(preflight.subprocess, "run", return_value=subprocess.CompletedProcess(
            (), 0, "123.0\n", "",
        )) as run:
            result = preflight._check_chromium(self.root, probe, browsers)
        self.assertIn("123.0", result)
        command = run.call_args.args[0]
        self.assertEqual(("node", "--input-type=module", "-e"), command[:3])
        self.assertEqual(probe.read_text(encoding="utf-8"), command[3])
        self.assertGreater(run.call_args.kwargs["timeout"], 0)
        environment = run.call_args.kwargs["env"]
        self.assertEqual(str(browsers), environment["PLAYWRIGHT_BROWSERS_PATH"])
        self.assertEqual("1", environment[preflight.IMAGE_DEADLINES])

    def test_cli_reports_failed_prerequisites_without_discovering_tests(self):
        argv = ["suite", "--phase", "preflight", "--project-root", str(self.root)]
        extensions = self.root / "custom-extensions"
        with (patch.object(runner.sys, "argv", argv),
              patch.dict(preflight.os.environ, {"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extensions)}),
              patch("sys.stderr", new_callable=io.StringIO) as stderr,
              patch.object(preflight, "_check_frontend", side_effect=ValueError("lock changed")),
              patch.object(preflight, "_check_duckpgq", side_effect=ValueError("load failed")),
              patch.object(preflight, "_check_chromium", side_effect=OSError("browser missing")),
              patch.object(runner, "discover_test_modules") as discover):
            self.assertEqual(1, runner.main())
        discover.assert_not_called()
        self.assertIn("npm ci", stderr.getvalue())
        self.assertIn(str(extensions), stderr.getvalue())
        self.assertIn("playwright-browsers", stderr.getvalue())
        report_path, = (self.root / ".anechoic_tmp/test_reports").glob("*.json")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(("failed", "preflight"), (report["status"], report["step"]))
        self.assertIn("load failed", report["error"])

    def test_preflight_uses_project_relative_cache_override_and_reports_success(self):
        report = {}
        with (patch.dict(preflight.os.environ, {"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": "relative/cache"}),
              patch("sys.stdout", new_callable=io.StringIO),
              patch.object(preflight, "_check_frontend", return_value="ready"),
              patch.object(preflight, "_check_duckpgq", return_value="loaded") as duckpgq,
              patch.object(preflight, "_check_chromium", return_value="launched")):
            self.assertEqual(0, runner.run_full_suite(self.root, phase="preflight", report=report))
        duckpgq.assert_called_once_with(self.root, self.root / "relative/cache")
        self.assertEqual({"step": "preflight"}, report)
