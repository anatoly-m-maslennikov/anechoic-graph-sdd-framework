(
    'Fast Functional selection retains whole packages and replays a Release '
    'seed.'
)

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.functional_history import (
    select_fast,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_cli import run_phase
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_report import (
    suite_report,
)
from unittest.mock import NonCallableMock


class FastSelectionTests(unittest.TestCase):
    def test_history_cutoff_replay_and_promotion(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / ".anechoic_tmp/test_reports"
            reports.mkdir(parents=True)
            now = datetime.now(timezone.utc)
            modules = [root / f"C{i}/C{i}__tests/functional/test_{n}.py" for i in range(12) for n in range(2)]
            def write(name, age, entries, **extra):
                record = {"started_at": (now - timedelta(days=age)).isoformat(),
                          "phase": "functional", "modules": entries, **extra}
                (reports / name).write_text(json.dumps(record))
            def failed(i):
                return [{"path": modules[i * 2].relative_to(root).as_posix(),
                         "status": "failed"}]
            write("recent.json", 6, failed(0))
            write("stale.json", 8, failed(1))
            with patch.dict(os.environ, {"ANECHOIC_FUNCTIONAL_SAMPLE_SEED": "run-a"}, clear=True):
                report = {}
                selected = select_fast(root, modules, report)
                choice = report["functional_selection"]
                self.assertEqual(["C0/C0__tests"], choice["hot_packages"])
                self.assertEqual(2, len(choice["sample_packages"]))
                packages = set(choice["hot_packages"] + choice["sample_packages"])
                self.assertEqual(3, len(packages))
                expected = [module for module in modules
                            if module.parent.parent.relative_to(root).as_posix() in packages]
                self.assertCountEqual(expected, selected)
                self.assertCountEqual([path.relative_to(root).as_posix() for path in expected],
                                      choice["selected_paths"])
                sample_index = int(choice["sample_packages"][0].split('/')[0][1:])
                write("replay.json", 0, [], functional_selection=choice)
                write("failure.json", 0, failed(sample_index))
                replay = {}
                self.assertEqual(selected, select_fast(root, modules, replay))
                self.assertEqual(choice["selected_packages"], replay["functional_selection"]["selected_packages"])
            with patch.dict(os.environ, {"ANECHOIC_FUNCTIONAL_SAMPLE_SEED": "run-b"}, clear=True):
                promoted = {}
                select_fast(root, modules, promoted)
                self.assertIn(choice["sample_packages"][0], promoted["functional_selection"]["hot_packages"])
                self.assertNotIn("C1/C1__tests", promoted["functional_selection"]["hot_packages"])

    def test_target_report_is_reused_as_history(self):
        with TemporaryDirectory() as source, TemporaryDirectory() as target:
            args = NonCallableMock(
                spec_set=[
                    'phase',
                    'test_modules',
                    'required',
                    'candidate_image',
                    'run_id',
                ],
                phase="functional",
                test_modules=None,
                required=False,
                candidate_image=None,
                run_id=None)
            module = Path(source) / "C/C__tests/test_failure.py"
            with patch.dict(os.environ, {"ANECHOIC_FUNCTIONAL_HISTORY_ROOT": target}, clear=True):
                with suite_report(Path(source), args) as report:
                    report["modules"].append({"path": "C/C__tests/test_failure.py", "status": "failed",
                                              "tests_run": 1, "skipped": 0})
                selection = {}
                self.assertEqual([module], select_fast(Path(source), [module], selection))
                self.assertEqual(["C/C__tests"], selection["functional_selection"]["hot_packages"])
                self.assertEqual(1, len(list((Path(target) / ".anechoic_tmp/test_reports").glob("*.json"))))

    def test_fast_rejected_for_nonfunctional_phase(self):
        args = NonCallableMock(
            spec_set=["phase", "functional_suite"],
            phase="unit",
            functional_suite="fast",
        )
        self.assertEqual(
            1, run_phase(Path.cwd(), args, {}, lambda *args, **kwargs: 0)
        )


if __name__ == "__main__":
    unittest.main()
