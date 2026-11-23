"""Verify phase classification and image gate ordering."""

import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import test_suite__shared as runner
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import _release_canary


class PhaseTests(unittest.TestCase):
    def test_phase_folders_and_legacy_modules(self):
        root = Path('/project')
        base = root / 'component' / 'component__tests'
        for relative, expected in (
            ('static/test_a.py', 'static'), ('unit/test_b.py', 'unit'),
            ('image/test_c.py', 'image'), ('test_old.py', 'unit'),
            ('assets/image/test_copy.py', 'unit'),
        ):
            self.assertEqual(expected, runner._test_phase(root, base / relative))
        self.assertEqual('image', runner._test_phase(root, root / runner.MCP_TESTS / 'test_a_docker_e2e.py'))

    def test_static_and_unit_select_separate_modules(self):
        root = Path('/project')
        base = root / 'component' / 'component__tests'
        static, unit, image = (base / phase / 'test_a.py' for phase in ('static', 'unit', 'image'))
        with (patch.object(runner, '_run_static_checks', return_value=0) as checks,
              patch.object(runner, 'discover_test_modules', return_value=[static, unit, image]),
              patch.object(runner, '_run_selected_modules', return_value=0) as selected):
            self.assertEqual(0, runner.run_full_suite(root, phase='static'))
            checks.assert_called_once_with(root)
            self.assertEqual([static], selected.call_args.args[1])
            self.assertEqual(0, runner.run_full_suite(root, phase='unit'))
            checks.assert_called_once_with(root)
            self.assertEqual([unit], selected.call_args.args[1])

    def test_image_runs_canary_after_passing_tests_only(self):
        image = 'sha256:' + 'a' * 64
        root = self.enterContext(TemporaryDirectory())
        argv = ['runner', '--project-root', root, '--phase', 'image', '--candidate-image', image,
                '--canary-package', '/tmp/package', '--canary-selection', '{}', '--run-id', 'run']
        with (patch.object(runner.sys, 'argv', argv),
              patch("sys.stderr", new_callable=io.StringIO),
              patch.object(runner, 'run_full_suite', return_value=0) as suite,
              patch.object(_release_canary, 'verify_candidate_image', return_value='endpoint') as canary):
            self.assertEqual(0, runner.main())
            suite.assert_called_once()
            canary.assert_called_once()
        with (patch.object(runner.sys, 'argv', argv),
              patch("sys.stderr", new_callable=io.StringIO),
              patch.object(runner, 'run_full_suite', return_value=1),
              patch.object(_release_canary, 'verify_candidate_image') as canary):
            self.assertEqual(1, runner.main())
            canary.assert_not_called()

    def test_image_rejects_incomplete_or_invalid_inputs(self):
        root = self.enterContext(TemporaryDirectory())
        valid = ['--candidate-image', 'sha256:' + 'a' * 64, '--canary-package', '/tmp/package',
                 '--canary-selection', '{}', '--run-id', 'run']
        for extra in ([], ['--candidate-image', 'latest'], valid + ['--required'],
                      valid + ['--test-module', 'test_a.py'], valid[:-2],
                      valid[:5] + ['bad json'] + valid[6:]):
            with (self.subTest(extra=extra),
                  patch.object(runner.sys, 'argv', ['runner', '--project-root', root, '--phase', 'image', *extra]),
                  patch("sys.stderr", new_callable=io.StringIO),
                  patch.object(runner, 'run_full_suite') as suite):
                self.assertEqual(1, runner.main())
                suite.assert_not_called()


if __name__ == '__main__':
    unittest.main()
