"""Check the admitted carrier models and the comparison failure boundary."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier_compare import compare  # fmt: skip
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier.carrier_formal import _PATHS, formal_inputs  # fmt: skip
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier.carrier_model import _SOURCE, generate  # fmt: skip


ROOT = Path(__file__).resolve().parents[6]
_DIRECT_PATHS = {
    "manifest": (
        Path(_PATHS["manifest"]).parent.parent
        / (
            "01_draft/AN-S-3069@63-draft-SPEC"
            "-COMPONENT_MANIFEST--declare-ada"
            "pters.md"
        )
    ),
    "solution": (
        Path(_PATHS["solution"]).parent
        / "AN-S-4742@2-draft-SWD-SOLUTION--extract-the-carrier-body.md"
    ),
}
SPEC = """import Lean
namespace CarrierBodyContract
inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving BEq
def bounds (_ : List Nat) : Option (Nat × Nat × Nat) := none
def body (_ : List Nat) : Outcome := .missingDelimiter
end CarrierBodyContract
"""


def _run_pinned_cli(request):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "pins.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                (
                    "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
                    "ENTATION_VERIFICATION_C74.carrie"
                    "r_compare"
                ),
                "--root",
                str(ROOT),
                "--pins",
                str(path),
            ],
            cwd=ROOT / "LAYER_4_ENGINE_STUDIO_C14",
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )


def _witness_pins():
    return {
        "manifest": {
            "path": _DIRECT_PATHS["manifest"].as_posix(),
            "atom_id": "AN-S-3069",
            "version": 63,
            "status": "draft",
            "container_component": "C16",
        },
        "solution": {
            "path": _DIRECT_PATHS["solution"].as_posix(),
            "atom_id": "AN-S-4742",
            "version": 2,
            "status": "draft",
            "container_component": "C30",
        },
    }


def _formal_witnesses():
    invalid = {"bounds": None, "body": None}
    pins = _witness_pins()
    return {
        "outcome": "compared",
        "translation": {"status": "bounded_match"},
        "lean": SPEC
        + SPEC.replace(
            "CarrierBodyContract", "CarrierBodySolution"
        ).removeprefix("import Lean\n"),
        "sources": {
            role: {
                **pin,
                "sha256": hashlib.sha256(
                    (ROOT / pin["path"]).read_bytes()
                ).hexdigest(),
            }
            for role, pin in pins.items()
        },
        "cases": [
            {
                "input": list(b"---\n---\n\xff"),
                "manifest": invalid,
                "solution": invalid,
            },
            {
                "input": list(b"---\n---"),
                "manifest": invalid,
                "solution": invalid,
            },
        ],
    }


def _pins(formal):
    return {
        role: {key: value for key, value in source.items() if key != "sha256"}
        for role, source in formal["sources"].items()
    }


def _test_live_source_and_analysis(self):
    model, evidence = generate(ROOT)
    self.assertIn("findClosing", model)
    self.assertEqual(
        set(evidence["symbols"]), {"frontmatter_bounds", "source_body"}
    )
    self.assertTrue(evidence["calls"])


def _test_unknown_source_fails_closed(self):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / _SOURCE
        target.parent.mkdir(parents=True)
        target.write_bytes(
            (ROOT / _SOURCE)
            .read_bytes()
            .replace(b"opening_end - 1", b"opening_end - 2")
        )
        with self.assertRaisesRegex(
            ValueError, "unsupported carrier operation"
        ):
            generate(tmp)


def _test_missing_lean_is_unresolved(self):
    with patch(
        (
            "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
            "ENTATION_VERIFICATION_C74.carrie"
            "r_compare.formal_inputs"
        ),
        return_value=([SPEC, SPEC], {}),
    ):
        report = compare(ROOT, "/missing/lean")
    self.assertEqual(report["status"], "unresolved")


def _test_unbound_solution_is_rejected(self):
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in _PATHS.items():
            target = Path(tmp) / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (ROOT / _DIRECT_PATHS[name]).read_bytes()
            target.write_bytes(
                data.replace(b"status: draft", b"status: active")
                if name == "manifest"
                else data
            )
        with self.assertRaisesRegex(ValueError, "binding"):
            formal_inputs(tmp)


def _test_embedded_contract_uses_manifest_hash(self):
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in _PATHS.items():
            target = Path(tmp) / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (ROOT / _DIRECT_PATHS[name]).read_bytes()
            data = (
                data.replace(b"status: draft", b"status: active")
                if name == "manifest"
                else data.replace(b"AN-S-3069@63-draft", b"AN-S-3069@63")
            )
            lean = b"\n```lean\n" + SPEC.encode() + b"```\n"
            data = (
                data + lean
                if name == "manifest"
                else data.replace(
                    b"### Formal Claim\n", b"### Formal Claim\n" + lean
                )
            )
            target.write_bytes(data)
        blocks, evidence = formal_inputs(tmp)
        self.assertEqual(
            evidence["manifest"]["sha256"], evidence["contract"]["sha256"]
        )
        self.assertEqual(
            evidence["manifest"]["atom_id"],
            evidence["contract"]["atom_id"],
        )
        self.assertEqual(len(blocks), 2)


def _test_duplicate_function_is_rejected(self):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / _SOURCE
        target.parent.mkdir(parents=True)
        target.write_bytes(
            (ROOT / _SOURCE).read_bytes() + b"\ndef source_body(): pass\n"
        )
        with self.assertRaisesRegex(
            ValueError, "unsupported carrier functions"
        ):
            generate(tmp)


def _test_extra_lean_output_is_unresolved(self):
    result = subprocess.CompletedProcess(
        [], 0, stdout="notice true\n[true]", stderr=""
    )
    with (
        patch("shutil.which", return_value="lean"),
        patch("subprocess.run", return_value=result),
        patch(
            (
                "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
                "ENTATION_VERIFICATION_C74.carrie"
                "r_compare.formal_inputs"
            ),
            return_value=([SPEC, SPEC], {}),
        ),
    ):
        report = compare(ROOT)
    self.assertEqual(report["status"], "unresolved")


def _test_direct_comparison_checks_the_python_oracle(self):
    formal = _formal_witnesses()
    pins = _pins(formal)

    def verify(root, component, manifest, *, solution, lean):
        self.assertEqual(
            (root, component, manifest, solution),
            (ROOT, "C30", pins["manifest"], pins["solution"]),
        )
        return formal

    report = compare(ROOT, **pins, formal_verifier=verify)
    self.assertEqual(report["status"], "mismatch", report["evidence"])
    self.assertEqual(
        report["findings"],
        [
            {
                "model": role,
                "case": 1,
                "raw": list(b"---\n---\n\xff"),
                "differences": ["bounds", "body"],
            }
            for role in ("manifest", "solution")
        ],
    )
    self.assertEqual(
        report["cases"][1]["error"],
        f"{Path('case-2/carrier-2.md')}: unsupported frontmatter delimiter",
    )
    self.assertTrue(all(row["code_matches_python"] for row in report["cases"]))


def _test_direct_comparison_rejects_different_solution_pin(self):
    formal = _formal_witnesses()
    pins = _pins(formal)
    pins["solution"].update(path=_PATHS["solution"], version=1)
    report = compare(ROOT, **pins, formal_verifier=lambda *a, **kw: formal)
    self.assertEqual(report["status"], "unresolved")
    self.assertEqual(
        report["evidence"]["unresolved"],
        ["Solution receipt does not match the requested pin"],
    )


def _test_direct_comparison_checks_both_formal_hashes(self):
    for role in ("manifest", "solution"):
        with self.subTest(role=role):
            formal = _formal_witnesses()
            formal["sources"][role]["sha256"] = "changed"
            report = compare(
                ROOT,
                **_pins(formal),
                formal_verifier=lambda *a, value=formal, **kw: value,
            )
            self.assertEqual(report["status"], "unresolved")
            self.assertEqual(
                report["evidence"]["unresolved"],
                [f"{role.title()} bytes changed after formal comparison"],
            )
