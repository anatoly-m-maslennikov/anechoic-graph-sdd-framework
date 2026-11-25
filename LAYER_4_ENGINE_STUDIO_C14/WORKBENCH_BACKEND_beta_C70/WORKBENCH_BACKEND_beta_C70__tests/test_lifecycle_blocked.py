import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from WORKBENCH_BACKEND_beta_C70.lifecycle_tools import _result


class LifecycleBlockedTests(unittest.TestCase):
    def test_preserves_blocked_write(self):
        error = {"code": "write_blocked", "message": "Lifecycle requires admission of the preceding write"}
        reply = {"lifecycle": {"outcome": "blocked", "errors": [error]},
                 "write_state": "known", "projection": {"state": "blocked"}}
        self.assertEqual({"status": "blocked", "effects": [], "warnings": [], "errors": [error]},
                         _result("atom_lifecycle_create_draft", reply))

    def test_blocked_projection_requires_blocked_write(self):
        reply = {"lifecycle": {"outcome": "completed"}, "write_state": "known",
                 "projection": {"state": "blocked"}}
        with self.assertRaises(ValueError):
            _result("atom_lifecycle_create_draft", reply)
