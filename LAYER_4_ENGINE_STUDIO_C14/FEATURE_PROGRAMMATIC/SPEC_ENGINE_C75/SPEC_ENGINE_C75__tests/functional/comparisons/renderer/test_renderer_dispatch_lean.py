"""Exercise the pinned public C87 implementation comparison."""

import hashlib
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ._renderer_dispatch_lean_support import (
    COMPONENT,
    SOURCE_NAMES,
    _compare,
    _pins,
    _stage,
    check_dispatch_mutations,
)


@unittest.skipUnless(
    all(
        os.environ.get(name)
        for name in ("AUTOFORM_CHECKOUT", "JOERN_HOME", "LEAN_PATH")
    ),
    "Autoform and its Lean libraries are not configured",
)
class RendererDispatchLeanTests(unittest.TestCase):
    def test_pinned_shape_runs_through_translated_dispatcher(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            export_path = COMPONENT / "_package__shared.py"
            export_digest = _stage(root, export_path)
            pins = _pins(root, "C87")
            request = {
                **pins,
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
                "export_sha256": export_digest,
            }
            status, report = _compare(root, request)
            self.assertEqual(0, status, report)
            self.assertEqual("no_mismatch_in_cases", report["status"], report)
            self.assertEqual(pins, report["sources"])
            self.assertEqual(request["witness"], report["witness"])
            self.assertEqual(
                {
                    (COMPONENT / name).as_posix(): digest
                    for name, digest in digests.items()
                },
                report["implementation"],
            )
            export = report["public_export"]
            self.assertEqual(
                (export_path.as_posix(), export_digest, "matched"),
                (export["path"], export["sha256"], export["status"]),
            )
            self.assertTrue(export["unresolved"] and report["unresolved"])
            self.assertEqual(
                ["matched", "matched"],
                [case["status"] for case in report["cases"]],
            )

            check_dispatch_mutations(self, root, digests, request)

    def test_blank_diagram_is_a_mismatch(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            export = _stage(root, COMPONENT / "_package__shared.py")
            dispatcher = root / COMPONENT / SOURCE_NAMES[0]
            original = dispatcher.read_bytes()
            returned = b"return shape_to_mermaid(claim)"
            self.assertEqual(original.count(returned), 1)
            changed = original.replace(returned, "return ' \u00a0 '".encode())
            dispatcher.write_bytes(changed)
            digests[SOURCE_NAMES[0]] = hashlib.sha256(changed).hexdigest()
            request = {
                **_pins(root, "C87"),
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
                "export_sha256": export,
            }
            status, report = _compare(root, request)
        self.assertEqual((1, "mismatch"), (status, report["status"]), report)
        self.assertEqual(
            ["conflicting", "conflicting"],
            [case["status"] for case in report["cases"]],
        )

    def test_missing_facade_leaves_the_renderer_unresolved(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            request = {
                **_pins(root, "C87"),
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
            }
            status, report = _compare(root, request)
        self.assertEqual((1, "unresolved"), (status, report["status"]), report)
        self.assertIn("_package__shared.py", json.dumps(report["unresolved"]))
        self.assertFalse(report["cases"])

    def test_renderer_must_accept_the_callers_action_keyword(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            export = _stage(root, COMPONENT / "_package__shared.py")
            dispatcher = root / COMPONENT / SOURCE_NAMES[0]
            original = dispatcher.read_bytes()
            signature = b"*, action=None, observe=None):"
            self.assertEqual(original.count(signature), 1)
            changed = original.replace(
                signature,
                b"*, selection=None, observe=None):\n    action = selection",
            )
            dispatcher.write_bytes(changed)
            digests[SOURCE_NAMES[0]] = hashlib.sha256(changed).hexdigest()
            request = {
                **_pins(root, "C87"),
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
                "export_sha256": export,
            }
            status, report = _compare(root, request)
        self.assertEqual((1, "mismatch"), (status, report["status"]), report)
        self.assertEqual(
            ["conflicting", "conflicting"],
            [case["status"] for case in report["cases"]],
        )
        self.assertEqual(
            [{"positional": "matched", "action_none": "conflicting"}] * 2,
            [case["calls"] for case in report["cases"]],
        )

    def test_unobserved_solution_guard_withholds_a_passing_result(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            export = _stage(root, COMPONENT / "_package__shared.py")
            pins = _pins(root, "C87")
            solution = root / pins["solution"]["path"]
            original = solution.read_bytes()
            guard = b"'kind': 'output',"
            self.assertEqual(original.count(guard), 1)
            changed = original.replace(
                guard,
                guard + b" 'detail': {'required_output_field': 'available'},",
            )
            solution.write_bytes(changed)
            pins["solution"]["sha256"] = hashlib.sha256(changed).hexdigest()
            request = {
                **pins,
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
                "export_sha256": export,
            }
            status, report = _compare(root, request)
        self.assertEqual((1, "unresolved"), (status, report["status"]), report)
        self.assertEqual(
            [{"positional": "matched", "action_none": "matched"}] * 2,
            [case["calls"] for case in report["cases"]],
        )
        self.assertIn("required_output_field", report["solution_gap"])
        self.assertIn(report["solution_gap"], report["unresolved"])

    def test_replay_rejects_a_changed_export_digest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            digests = {
                name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES
            }
            export = COMPONENT / "_package__shared.py"
            expected = _stage(root, export)
            with (root / export).open("ab") as file:
                file.write(b"\n")
            request = {
                **_pins(root, "C87"),
                "witness": _pins(root, "C52"),
                "implementation_sha256": digests,
                "export_sha256": expected,
            }
            status, report = _compare(root, request)
        self.assertEqual((1, "unresolved"), (status, report["status"]), report)
        self.assertIn(
            "Public export source digest changed",
            json.dumps(report["unresolved"]),
        )
        self.assertFalse(report["cases"])
