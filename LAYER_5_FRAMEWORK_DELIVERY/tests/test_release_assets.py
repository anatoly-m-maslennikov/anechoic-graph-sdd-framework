"""Native release asset checks retain the compatibility boundary."""
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
        wb = self.package / 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND'
        lifecycle = self.package / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE'
        self.assets = tuple(directory / name for directory, name in (
            (wb, 'canonical_relation_registry.json'), (wb, 'workbench_schema.json'),
            (lifecycle, 'status_model.json'), (lifecycle, 'candidate_schema.json'),
        ))
        for path in self.assets:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}')

    def test_validates_native_project_and_retains_compatibility_assets(self):
        with patch('release_assets.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(self.assets, verify_native_release_assets(self.package, self.root, Path('.anechoic_project')))
        args, kwargs = run.call_args
        self.assertIn('bind_status_specifications', args[0][3])
        self.assertIn('load_native_inputs', args[0][3])
        self.assertEqual((str(self.package), str(self.root), '.anechoic_project'), args[0][4:])
        self.assertEqual(60, kwargs['timeout'])

    def test_missing_symlink_failed_and_timed_out_checks_refuse(self):
        with patch('release_assets.subprocess.run') as run:
            self.assets[0].unlink()
            with self.assertRaisesRegex(LocalReleaseError, 'native-assets-unavailable'):
                verify_native_release_assets(self.package, self.root, Path('.anechoic_project'))
            self.assets[0].symlink_to(self.assets[1])
            with self.assertRaisesRegex(LocalReleaseError, 'native-assets-unavailable'):
                verify_native_release_assets(self.package, self.root, Path('.anechoic_project'))
            run.assert_not_called()
        self.assets[0].unlink()
        self.assets[0].write_text('{}')
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
