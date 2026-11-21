"""Verify native release inputs."""
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'RELEASE_VERSION'))
from release_assets import LocalReleaseError, verify_native_release_assets  # noqa: E402


class NativeReleaseAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'package'

    def test_validates_native_project_without_legacy_assets(self):
        with patch('release_assets.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run:
            verify_native_release_assets(self.package, self.root, Path('.anechoic_project'))
        args, kwargs = run.call_args
        self.assertIn('bind_status_specifications', args[0][3])
        self.assertIn('compile_structure', args[0][3])
        self.assertNotIn('load_native_inputs', args[0][3])
        self.assertEqual((str(self.package), str(self.root), '.anechoic_project'), args[0][4:])
        self.assertEqual(60, kwargs['timeout'])

    def test_failed_and_timed_out_checks_refuse(self):
        for outcome in (SimpleNamespace(returncode=1), subprocess.TimeoutExpired('verify', 60)):
            with self.subTest(outcome=outcome), patch('release_assets.subprocess.run') as run:
                if isinstance(outcome, Exception):
                    run.side_effect = outcome
                else:
                    run.return_value = outcome
                with self.assertRaisesRegex(LocalReleaseError, 'native-assets-verification-failed'):
                    verify_native_release_assets(self.package, self.root, Path('.anechoic_project'))


if __name__ == '__main__':
    unittest.main()
