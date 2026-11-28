"""Check the published Diagnostics contract against fresh Autoform Lean."""

import hashlib
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ._diagnostic_lean_comparison_support import (
    ROOT,
    SOURCE,
    _compare,
    _pinned_specs,
    _stage,
    check_finding_mutant,
    check_rebound_facade,
)


@unittest.skipUnless(
    all(
        os.environ.get(name)
        for name in ("AUTOFORM_CHECKOUT", "JOERN_HOME", "LEAN_PATH")
    ),
    "Autoform and its Lean libraries are not configured",
)
class DiagnosticLeanComparisonTests(unittest.TestCase):
    def test_shared_verdict_matches_policy_for_any_status_list(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        original = b'return (\n        "conflicting"'
        mutated = (
            b'return (\n        "unresolved"\n'
            b'        if "unresolved" in statuses\n'
            b'        else "conflicting"'
        )
        self.assertEqual(1, source.count(original))
        changed = source.replace(original, mutated)
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            path = folder / "pins.json"
            code, control = _compare(pins, source, ROOT, path)
            root = folder / "mutation"
            _stage(root, pins, changed)
            result, report = _compare(pins, changed, root, path)
        self.assertEqual(
            (0, "no_mismatch_in_cases"), (code, control["status"]), control
        )
        self.assertEqual("proved", control["verdict_proof"]["status"], control)
        self.assertEqual(
            "publicVerdictMatchesContract", control["verdict_proof"]["theorem"]
        )
        self.assertRegex(control["verdict_proof"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(
            control["verdict_proof"]["authored_lean_sha256"], r"^[0-9a-f]{64}$"
        )
        self.assertEqual((1, "unresolved"), (result, report["status"]), report)
        self.assertEqual("unresolved", report["verdict_proof"]["status"])
        self.assertEqual("proved", report["effect"]["status"])
        self.assertEqual(
            ["matched"] * 3, [row["implementation"] for row in report["facts"]]
        )

    def test_agreeing_changed_verdict_specs_cannot_prove_original_code(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        pending = b"'unresolved_or_empty': True"
        clear = b"'unresolved_or_empty': False"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            for pin in pins.values():
                path = root / pin["path"]
                original = path.read_bytes()
                self.assertEqual(
                    (1, 1), (original.count(pending), original.count(clear))
                )
                changed = original.replace(pending, b"PLACEHOLDER", 1)
                changed = changed.replace(clear, pending, 1)
                changed = changed.replace(b"PLACEHOLDER", clear, 1)
                path.write_bytes(changed)
                pin["sha256"] = hashlib.sha256(changed).hexdigest()
            code, report = _compare(pins, source, root, root / "pins.json")
        self.assertEqual((1, "unresolved"), (code, report["status"]), report)
        self.assertEqual("proved", report["effect"]["status"])
        verdict = report["verdict_proof"]
        self.assertEqual("unresolved", verdict["status"])
        self.assertRegex(verdict["authored_lean_sha256"], r"^[0-9a-f]{64}$")

    def test_extra_verdict_solution_guard_leaves_proof_unresolved(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins["solution"]["path"]
            original = path.read_bytes()
            guard = b"{'has_conflict': True}"
            self.assertEqual(1, original.count(guard))
            changed = original.replace(
                guard, b"{'has_conflict': True, 'unresolved_or_empty': True}"
            )
            path.write_bytes(changed)
            pins["solution"]["sha256"] = hashlib.sha256(changed).hexdigest()
            code, report = _compare(pins, source, root, root / "pins.json")
        self.assertEqual((1, "unresolved"), (code, report["status"]), report)
        self.assertEqual("proved", report["effect"]["status"])
        verdict = report["verdict_proof"]
        self.assertEqual("unresolved", verdict["status"])
        self.assertRegex(verdict["authored_lean_sha256"], r"^[0-9a-f]{64}$")

    def test_cli_checks_declared_values_and_detects_wrong_field(self):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        self.assertEqual(source.count(b'"message": message'), 1)
        mutant = source.replace(b'"message": message', b'"message": field')
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            request_path = folder / "pins.json"
            check_finding_mutant(
                self, pins, source, mutant, folder, request_path
            )

            fields = b'"source": source, "field": field'
            self.assertEqual(source.count(fields), 1)
            reordered = source.replace(
                fields, b'"field": field, "source": source'
            )
            root = folder / "reordered"
            _stage(root, pins, reordered)
            status, report = _compare(pins, reordered, root, request_path)
            self.assertEqual(
                (0, "proved"), (status, report["proof"]["status"]), report
            )

    def test_cli_leaves_a_solution_with_an_unguarded_alternative_unresolved(
        self,
    ):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins["solution"]["path"]
            text = path.read_text(encoding="utf-8")
            state = "            'returning': {'on': {"
            self.assertEqual(text.count(state), 1)
            alternative = (
                "            'returning': {'on': {\n"
                "                'return_unchecked': {'target': 'done', "
                "'guard': {'type': 'matchesTrace',\n"
                "                    'params': {'kind': 'output', "
                "'outcome': 'reported'}}},\n"
            )
            data = text.replace(state, alternative).encode()
            path.write_bytes(data)
            pins["solution"]["sha256"] = hashlib.sha256(data).hexdigest()
            status, report = _compare(pins, source, root, root / "pins.json")
            self.assertEqual(status, 1, report)
            self.assertEqual(report["status"], "unresolved")
            self.assertEqual(len(report["facts"]), 3)
            self.assertTrue(
                all(
                    row["solution"] == "unresolved"
                    and row["implementation"] == "matched"
                    for row in report["facts"]
                ),
                report,
            )

    def test_finding_proof_checks_inputs_outside_the_string_witness(self):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        self.assertEqual(source.count(b'"message": message'), 1)
        mutant = source.replace(
            b'"message": message',
            b'"message": field if message == "other" else message',
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, mutant)
            status, report = _compare(pins, mutant, root, root / "pins.json")
            self.assertEqual(
                (1, "unresolved"), (status, report["status"]), report
            )
            self.assertEqual("unresolved", report["proof"]["status"], report)
            self.assertEqual("unresolved", report["effect"]["status"])
            self.assertEqual(len(report["facts"]), 3)
            self.assertTrue(
                all(
                    row["implementation"] == "matched"
                    for row in report["facts"]
                ),
                report,
            )

    def test_rebound_facade_leaves_finding_unresolved(self):
        check_rebound_facade(self)

    def test_formation_conflict_is_visible_when_values_match(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins["solution"]["path"]
            original = path.read_bytes()
            changed = original.replace(
                b"'outcome': 'formed'", b"'outcome': 'emitted'"
            )
            self.assertNotEqual(original, changed)
            path.write_bytes(changed)
            pins["solution"]["sha256"] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / "pins.json")
            manifest = root / pins["manifest"]["path"]
            raw = manifest.read_bytes()
            changed = raw.replace(b"'formed'", b"'emitted'")
            self.assertNotEqual(raw, changed)
            manifest.write_bytes(changed)
            pins["manifest"]["sha256"] = hashlib.sha256(changed).hexdigest()
            code, unmeasured = _compare(pins, source, root, root / "pins.json")
        self.assertEqual((1, "mismatch"), (status, report["status"]), report)
        self.assertEqual("conflicting", report["effect"]["status"])
        self.assertTrue(report["facts"])
        self.assertTrue(
            all(row["implementation"] == "matched" for row in report["facts"])
        )
        self.assertEqual(
            (1, "unresolved"), (code, unmeasured["status"]), unmeasured
        )
        self.assertEqual("proved", unmeasured["proof"]["status"])
        self.assertEqual("unresolved", unmeasured["effect"]["status"])

    def test_unmeasured_output_guard_leaves_formation_unresolved(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins["solution"]["path"]
            original = path.read_bytes()
            changed = original.replace(
                b"'same_as': {", b"'same_as': {'unreturned_field': 'source', "
            )
            self.assertNotEqual(original, changed)
            path.write_bytes(changed)
            pins["solution"]["sha256"] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / "pins.json")
        self.assertEqual((1, "unresolved"), (status, report["status"]), report)
        self.assertEqual("proved", report["proof"]["status"])
        self.assertEqual("unresolved", report["effect"]["status"])

    def test_unmeasured_contract_type_prevents_a_pass(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins["manifest"]["path"]
            original = path.read_bytes()
            prefix = b"    same_values=("
            self.assertEqual(original.count(prefix), 1)
            changed = original.replace(
                prefix,
                b"    value_types={('result_returned', 'message'): "
                b"'integer'},\n" + prefix,
            )
            path.write_bytes(changed)
            pins["manifest"]["sha256"] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / "pins.json")
        self.assertEqual((1, "unresolved"), (status, report["status"]), report)
        self.assertEqual("proved", report["effect"]["status"])
        self.assertEqual(
            [
                {
                    "direction": "manifest_solution",
                    "action": "finding",
                    "key": "value_types",
                    "field": ["result_returned", "message"],
                    "expected": "integer",
                    "status": "unresolved",
                    "output": "reported",
                }
            ],
            report["unresolved_obligations"],
        )
