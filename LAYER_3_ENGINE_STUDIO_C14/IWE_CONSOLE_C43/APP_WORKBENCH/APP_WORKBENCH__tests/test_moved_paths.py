"""Check paths used by the relocated Workbench in a checkout or image."""

from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1]
STUDIO = APP.parents[1]


class MovedPathsTests(unittest.TestCase):
    def test_checkout_paths(self):
        self.assertEqual(APP, STUDIO / 'IWE_CONSOLE_C43/APP_WORKBENCH')
        self.assertTrue((STUDIO / 'FEATURE_PROGRAMMATIC/FEATURE_TOOLS').is_dir())
        self.assertTrue((STUDIO / 'MCP_PATCHBAY_C21/FEATURE_MCP').is_dir())
        self.assertTrue((APP / 'FEATURE_WORKBENCH_FRONTEND/package.json').is_file())


if __name__ == '__main__':
    unittest.main()
