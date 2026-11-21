"""Check paths used by the relocated Workbench in a checkout or image."""
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb

APP = Path(__file__).resolve().parents[1]
STUDIO = APP.parents[1]
sys.path.insert(0, str(APP.parent))

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.spec_trace import PILOT, SpecTraceStore


class MovedPathsTests(unittest.TestCase):
    def test_checkout_paths_and_trace_projection(self):
        self.assertEqual(APP, STUDIO.parent / PILOT)
        self.assertTrue((STUDIO / 'FEATURE_PROGRAMMATIC/FEATURE_TOOLS').is_dir())
        self.assertTrue((STUDIO / 'MCP_PATCHBAY_C21/FEATURE_MCP').is_dir())
        self.assertTrue((APP / 'FEATURE_WORKBENCH_FRONTEND/package.json').is_file())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / PILOT / 'example.py'
            module.parent.mkdir(parents=True)
            module.write_text('pass\n')
            module.with_name('example.py.spec_trace.md').write_text('## Implements\n\n- AN-S-501@1\n')
            connection = duckdb.connect(':memory:')
            self.addCleanup(connection.close)
            store = SpecTraceStore(connection, root)
            store.initialize()
            store.refresh()
            self.assertEqual(connection.execute('SELECT atom_id, version FROM implementation_rmedo').fetchall(),
                             [('AN-S-501', 1)])


if __name__ == '__main__':
    unittest.main()
