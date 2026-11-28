"""Pinned sources and staging for diagnostic comparison tests."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[7]
STUDIO = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
FORMAL = Path("SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94")
CARRIERS = (
    Path(
        "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15"
    )
    / FORMAL
)
SOURCE = (
    STUDIO
    / "FEATURE_PROGRAMMATIC"
    / FORMAL
    / "LAYER_1_DIAGNOSTICS_C90/diagnostics__pub.py"
)
EXPORT = SOURCE.with_name("_package__shared.py")
CLI = (
    "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare"
)
PINS = {
    "manifest": {
        "path": (
            CARRIERS
            / "01_TIER_1_ARCHITECTURE/AN-S-4937-SPEC-COMPONENT_MANIFEST"
            "--declare-diagnostics.md"
        ).as_posix(),
        "atom_id": "AN-S-4937",
        "version": 4,
        "status": "active",
        "container_component": "C94",
    },
    "solution": {
        "path": (
            CARRIERS / "LAYER_1_DIAGNOSTICS_C90/AN-S-5024-DES-SOLUTION"
            "--form-a-diagnostic-from-a-finding.md"
        ).as_posix(),
        "atom_id": "AN-S-5024",
        "version": 4,
        "status": "active",
        "container_component": "C90",
    },
}


def _compare(pins, source, root, request_path, *, export_sha256=None):
    request = {
        **pins,
        "implementation_sha256": hashlib.sha256(source).hexdigest(),
    }
    if export_sha256 is not None:
        request["export_sha256"] = export_sha256
    request_path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            CLI,
            "--root",
            str(root),
            "--component",
            "C90",
            "--pins",
            str(request_path),
            "--lean",
            os.environ.get("ANECHOIC_TEST_LEAN", "lean"),
        ],
        cwd=STUDIO,
        capture_output=True,
        text=True,
        timeout=2000,
        check=False,
    )
    return result.returncode, json.loads(result.stdout)


def _pinned_specs():
    return {
        role: {
            **pin,
            "sha256": hashlib.sha256(
                (ROOT / pin["path"]).read_bytes()
            ).hexdigest(),
        }
        for role, pin in PINS.items()
    }


def _stage(root, pins, source):
    for pin in pins.values():
        target = root / pin["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / pin["path"]).read_bytes())
    target = root / SOURCE.relative_to(ROOT)
    target.parent.mkdir(parents=True)
    target.write_bytes(source)
    target.with_name(EXPORT.name).write_bytes(EXPORT.read_bytes())


def check_finding_mutant(self, pins, source, mutant, folder, request_path):
    digest = hashlib.sha256(EXPORT.read_bytes()).hexdigest()
    status, control = _compare(
        pins, source, ROOT, request_path, export_sha256=digest
    )
    self.assertEqual(status, 0, control)
    self.assertEqual(control["formal"]["sources"], pins)
    self.assertEqual(control["formal"]["translation"]["status"], "matched")
    self.assertEqual(control["status"], "no_mismatch_in_cases")
    self.assertEqual("proved", control["proof"]["status"], control)
    self.assertEqual(
        {
            "target": "C90.source_diagnostic",
            "outcome": "formed",
            "status": "proved",
        },
        control["effect"],
    )
    self.assertEqual("matched", control["public_export"]["status"], control)
    self.assertTrue(control["unresolved"])
    checked = {tuple(row["right"]): row for row in control["facts"]}
    fields = {
        ("result_returned", name) for name in ("source", "field", "message")
    }
    self.assertEqual(set(checked), fields)
    for row in checked.values():
        self.assertEqual(row["solution"], "matched")
        self.assertEqual(row["implementation"], "matched")
    root = folder / "mutation"
    _stage(root, pins, mutant)
    status, mutated = _compare(pins, mutant, root, request_path)
    self.assertEqual(status, 1, mutated)
    self.assertEqual(mutated["status"], "mismatch")
    self.assertEqual(
        [
            (row["right"], row["solution"])
            for row in mutated["facts"]
            if row["implementation"] == "conflicting"
        ],
        [(["result_returned", "message"], "matched")],
    )


def check_rebound_facade(self):
    pins, source = _pinned_specs(), SOURCE.read_bytes()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        _stage(root, pins, source)
        facade = root / EXPORT.relative_to(ROOT)
        original = facade.read_bytes()
        changed = original.replace(
            b"finding as finding", b"verdict as finding"
        )
        self.assertNotEqual(original, changed)
        facade.write_bytes(changed)
        digest = hashlib.sha256(original).hexdigest()
        exit_code, stale = _compare(
            pins, source, root, root / "pins.json", export_sha256=digest
        )
        self.assertEqual(
            (1, "unresolved"), (exit_code, stale["status"]), stale
        )
        self.assertIn(
            "Public export source digest changed",
            json.dumps(stale["unresolved"]),
        )
        self.assertFalse(stale["facts"])
        status, report = _compare(pins, source, root, root / "pins.json")
    self.assertEqual((1, "unresolved"), (status, report["status"]), report)
    self.assertEqual(
        hashlib.sha256(changed).hexdigest(),
        report["public_export"]["sha256"],
    )
    self.assertIn(
        "Declared public export does not bind",
        json.dumps(report["unresolved"]),
    )
    self.assertIn(
        "diagnostics__pub.py:<module>.verdict",
        json.dumps(report["unresolved"]),
    )
    self.assertFalse(report["facts"])
