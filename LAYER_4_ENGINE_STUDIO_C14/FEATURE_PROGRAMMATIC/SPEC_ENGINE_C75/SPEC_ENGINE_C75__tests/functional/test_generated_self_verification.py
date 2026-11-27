import hashlib
import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95._package__shared import (
    SpecSnapshot,
)

ROOT = Path(__file__).resolve().parents[5]
BASE = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/'
PINS = (
    {
        "path": BASE
        + "01_draft/AN-S-5020@3-draft-SPEC-COMPONENT_MANIFEST--declare-formal-specification.md",
        "atom_id": "AN-S-5020",
        "version": 3,
        "status": "draft",
        "container_component": "C75",
    },
    {
        "path": BASE
        + "LAYER_2_FORMAL_SPECIFICATION_C94/01_draft/AN-S-5035@1-draft-DES-SOLUTION--verify-a-pinned-formal-chain.md",
        "atom_id": "AN-S-5035",
        "version": 1,
        "status": "draft",
        "container_component": "C94",
    },
)
ACTION = 'verify_pinned_specs'


def _snapshot_rows(root=ROOT):
    rows = []
    for pin in PINS:
        path = root / pin['path']
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        digest = hashlib.sha256(raw).hexdigest()
        rows.append(
            {
                "source_path": pin["path"],
                "exact_ref": f"{pin['atom_id']}@{pin['version']}-draft",
                "metadata": carrier.metadata,
                "body": carrier.body,
                "sha256": digest,
            }
        )
    return rows


class GeneratedSelfVerificationTests(unittest.TestCase):
    def test_receipt_pins_replay_only_the_same_carrier_bytes(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for pin in PINS:
                path = root / pin['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / pin["path"]).read_bytes())
            original = verify_formal_chain(
                root,
                "C94",
                PINS[0],
                solution=PINS[1],
                action=ACTION,
                lean=lean,
            )
            self.assertEqual("compared", original["outcome"], original)
            evidence = original["evidence"]
            pins = evidence["sources"]
            for reader in (root, SpecSnapshot(_snapshot_rows(root))):
                replay = verify_formal_chain(
                    reader, "C94", **pins, action=ACTION, lean=lean
                )
                self.assertEqual("compared", replay["outcome"], replay)
                self.assertEqual(evidence, replay["evidence"])
            path = root / pins["solution"]["path"]
            with path.open("ab") as file:
                file.write(b"\nA same-version prose edit.\n")
            for reader in (root, SpecSnapshot(_snapshot_rows(root))):
                stale = verify_formal_chain(
                    reader, "C94", **pins, action=ACTION, lean="/missing/lean"
                )
                self.assertEqual("incomplete", stale["outcome"], stale)
                (diagnostic,) = stale["diagnostics"]
                self.assertEqual(
                    ("solution", "sha256"),
                    (diagnostic["role"], diagnostic["field"]),
                )
                self.assertEqual(pins["solution"], diagnostic["source"])
                self.assertNotIn("evidence", stale)

    def test_generated_contrary_effects_and_stale_pin(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        rows = _snapshot_rows()
        snapshot = SpecSnapshot(rows)
        nominal = verify_formal_chain(
            snapshot,
            "C94",
            PINS[0],
            solution=PINS[1],
            action=ACTION,
            lean=lean,
        )
        self.assertEqual("compared", nominal["outcome"], nominal)
        facts = nominal["evidence"]["coverage"]
        self.assertNotIn("conflicting", [fact["status"] for fact in facts])
        effects = {
            fact["output"]: fact["left"][:2]
            for fact in facts
            if fact["direction"] == "manifest_solution"
            and fact["key"] == "must_effect"
            and fact["status"] == "matched"
        }
        self.assertEqual({"compared", "incomplete"}, effects.keys())
        for output, (target, outcome) in effects.items():
            with self.subTest(output=output, target=target):
                original = f"'target': {target!r}, 'outcome': {outcome!r}"
                changed = f"'target': {target!r}, 'outcome': 'generated_contrary'"
                self.assertIn(original, rows[1]['body'])
                body = rows[1]['body'].replace(original, changed)
                solution = {**rows[1], 'body': body, 'sha256': hashlib.sha256(body.encode()).hexdigest()}
                result = verify_formal_chain(SpecSnapshot([rows[0], solution]), 'C94', PINS[0],
                                             solution=PINS[1], action=ACTION, lean=lean)
                self.assertEqual('compared', result['outcome'], result)
                comparison = result['directions']['manifest_solution']
                self.assertEqual('conflicting', comparison['status'], result)
                self.assertTrue(any(fact['output'] == output and fact['key'] == 'must_effect'
                                    and fact['left'][:2] == (target, outcome) and fact['status'] == 'conflicting'
                                    for fact in comparison['facts'] if 'output' in fact))
                self.assertTrue(result['evidence']['comparison_programs'])
        stale = {**PINS[1], 'version': PINS[1]['version'] + 1}
        result = verify_formal_chain(snapshot, 'C94', PINS[0], solution=stale, action=ACTION, lean=lean)
        self.assertEqual('incomplete', result['outcome'], result)
        self.assertEqual('exact_ref', result['diagnostics'][0]['field'])

    def test_missing_selected_action_reports_its_pinned_source(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        rows = _snapshot_rows()
        path = ROOT / PINS[1]['path']
        raw = path.read_bytes()
        changed = raw.replace(
            f"action='{ACTION}'".encode(), b"action='renamed_verify'", 1
        )
        self.assertNotEqual(raw, changed)
        rows[1].update(
            body=parse_carrier(changed, path).body,
            sha256=hashlib.sha256(changed).hexdigest(),
        )
        pins = [
            {**pin, "sha256": row["sha256"]}
            for pin, row in zip(PINS, rows, strict=True)
        ]
        snapshot = SpecSnapshot(rows)
        for action, source, field in (
            (ACTION, pins[1], "mermaid"),
            ("unknown", pins[0], "action"),
        ):
            with self.subTest(action=action):
                result = verify_formal_chain(
                    snapshot, "C94", *pins, action=action, lean=lean
                )
                self.assertEqual("incomplete", result["outcome"], result)
                (diagnostic,) = result["diagnostics"]
                self.assertEqual(
                    (source, field),
                    (diagnostic["source"], diagnostic["field"]),
                )
                self.assertNotIn("evidence", result)

    def test_blank_renderer_output_stops_before_comparison(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        rows = _snapshot_rows()
        pins = [
            {**pin, "sha256": row["sha256"]}
            for pin, row in zip(PINS, rows, strict=True)
        ]
        base = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub"
        with (
            patch(f"{base}.render_solution", return_value=" \n"),
            patch(f"{base}.compare_trace_spec") as compare,
        ):
            result = verify_formal_chain(
                SpecSnapshot(rows), "C94", *pins, action=ACTION, lean=lean
            )
        compare.assert_not_called()
        self.assertEqual("incomplete", result["outcome"], result)
        (diagnostic,) = result["diagnostics"]
        self.assertEqual(
            (pins[1], "mermaid"), (diagnostic["source"], diagnostic["field"])
        )
        self.assertNotIn("evidence", result)

    def test_malformed_snapshot_headers_report_the_exact_field(self):
        for index, field in ((0, 'context'), (1, 'context'), (1, 'relations')):
            with self.subTest(index=index, field=field):
                rows = _snapshot_rows()
                rows[index]["metadata"][field] = []
                result = verify_formal_chain(
                    SpecSnapshot(rows),
                    "C94",
                    PINS[0],
                    solution=PINS[1],
                    action=ACTION,
                )
                self.assertEqual("incomplete", result["outcome"], result)
                self.assertEqual(field, result["diagnostics"][0]["field"])
                self.assertEqual(
                    PINS[index]["path"],
                    result["diagnostics"][0]["source"]["path"],
                )

    def test_unavailable_lean_preserves_the_admitted_source_pin(self):
        rows = _snapshot_rows()
        lean = ROOT / "unavailable-lean"
        result = verify_formal_chain(
            SpecSnapshot(rows),
            "C94",
            PINS[0],
            solution=PINS[1],
            action=ACTION,
            lean=str(lean),
        )
        self.assertEqual("incomplete", result["outcome"], result)
        (diagnostic,) = result["diagnostics"]
        self.assertEqual("translation", diagnostic["field"])
        self.assertEqual(
            {**PINS[0], "sha256": rows[0]["sha256"]}, diagnostic["source"]
        )

    def test_missing_solution_pin_keeps_the_request_manifest_as_context(self):
        result = verify_formal_chain(
            SpecSnapshot(_snapshot_rows()), "C94", PINS[0], action=ACTION
        )
        self.assertEqual("incomplete", result["outcome"], result)
        (diagnostic,) = result["diagnostics"]
        self.assertEqual("solution", diagnostic["role"])
        self.assertEqual("source_pin", diagnostic["field"])
        self.assertEqual(PINS[0], diagnostic["source"])
