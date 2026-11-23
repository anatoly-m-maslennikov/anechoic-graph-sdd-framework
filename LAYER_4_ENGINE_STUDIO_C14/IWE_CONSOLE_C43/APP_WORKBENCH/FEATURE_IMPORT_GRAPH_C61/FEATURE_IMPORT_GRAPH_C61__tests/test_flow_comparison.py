import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest


LEAN = os.environ.get("LEAN_BIN") or shutil.which("lean")
SCRIPT = Path(__file__).resolve().parents[1] / "FlowComparison.lean"


def event(**changes):
    value = dict(kind="write", name="value", target="store", outcome="ok", detail={"value": 1})
    value.update(changes)
    return value


@unittest.skipUnless(LEAN, "Lean is not installed")
class FlowComparisonTests(unittest.TestCase):
    def compare(self, left, right, aligned=True, left_complete=True, right_complete=True):
        payload = {"inputsAligned": aligned,
                   "left": {"complete": left_complete, "events": left},
                   "right": {"complete": right_complete, "events": right}}
        process = subprocess.run([LEAN, "--run", str(SCRIPT)], input=json.dumps(payload),
                                 text=True, capture_output=True, check=True)
        return json.loads(process.stdout)

    def test_matching_and_repeated_effects(self):
        a = event(target=None, outcome=None)
        self.assertEqual(self.compare([a, a], [a, a])["status"], "matched")
        self.assertEqual(self.compare([event(detail={"a": 1, "b": 2})],
                                      [event(detail={"b": 2, "a": 1})])["status"], "matched")
        difference = self.compare([a, a], [a])
        self.assertEqual(difference["status"], "different")
        self.assertEqual(difference["firstDifference"]["index"], 1)
        self.assertIsNone(difference["firstDifference"]["right"])

    def test_order_error_target_and_detail(self):
        a, b = event(), event(name="other")
        self.assertEqual(self.compare([a, b], [b, a])["firstDifference"]["index"], 0)
        for changed in (event(outcome="error"), event(target="other"), event(detail={"value": 2})):
            with self.subTest(changed=changed):
                self.assertEqual(self.compare([a], [changed])["status"], "different")

    def test_incomplete_or_unaligned_is_unresolved(self):
        for options in ({"aligned": False}, {"left_complete": False}, {"right_complete": False}):
            with self.subTest(options=options):
                self.assertEqual(self.compare([event()], [], **options)["status"], "unresolved")

    def test_missing_required_event_field_is_rejected(self):
        payload = {"inputsAligned": True, "left": {"complete": True, "events": [{"kind": "effect", "name": "x", "outcome": None, "detail": {}}]},
                   "right": {"complete": True, "events": []}}
        process = subprocess.run([LEAN, "--run", str(SCRIPT)], input=json.dumps(payload),
                                 text=True, capture_output=True)
        self.assertNotEqual(process.returncode, 0)
        payload["left"]["events"] = [event(detail="not an object")]
        process = subprocess.run([LEAN, "--run", str(SCRIPT)], input=json.dumps(payload),
                                 text=True, capture_output=True)
        self.assertNotEqual(process.returncode, 0)
